"""CP-SAT solver: O(n^2) edge variables instead of O(n!).

Model:
  x[v,t,i,j] in {0,1} - vehicle v, trip t uses edge i->j (including return to farm)
  y[v,t,j] in {0,1} - buyer j is visited in trip t
  z[v,t,j,pi] >= 0 - kg of product pi to buyer j

Subtours: AddCircuit per outing, with self-loops for unused nodes.
Arrival is travel plus unload_seconds_per_kg times kg (including this stop).
Return to farm is in fuel cost, not in shelf life.
z is bounded by incoming edges, not only through y.
"""

from ortools.sat.python import cp_model

from app.demo_data import ASSUMPTIONS
from app.routing import fuel_cost_rub
from app.schemas import (
    PlanRequest,
    PlanResponse,
    ProductBalance,
    Shipment,
    SolverStatus,
    Stop,
    Trip,
)

OBJECTIVE = "maximize_profit"
LOAD_EPS = 1e-3
FARM = "farm"
HOUR_SECONDS = 3600


def _hours_to_int(hours: float) -> int:
    return int(round(hours * HOUR_SECONDS))


def _hop(graph: dict[tuple[str, str], tuple[float, float]], origin: str, dest: str):
    direct = graph.get((origin, dest))
    if direct is not None:
        return direct
    return graph.get((dest, origin))


def _vehicle_signature(vehicle) -> tuple:
    return (
        round(vehicle.capacity_kg, 6),
        round(vehicle.fuel_consumption_l_per_100km, 6),
        round(vehicle.fuel_price_rub_per_liter, 6),
        vehicle.max_trips,
        vehicle.max_stops,
    )


def solve_plan(request, graph, time_limit_seconds: float | None = 120):
    """Builds a profit-maximizing plan using CP-SAT with edge variables.

    time_limit_seconds: лимит поиска. 0 или None — без лимита.
    """
    orders = {
        (b.id, o.product_id): o
        for b in request.buyers
        for o in b.orders
    }
    products = list(request.products)
    buyers = list(request.buyers)
    buyer_ids = [b.id for b in buyers]
    product_index = {p.id: i for i, p in enumerate(products)}
    vehicles = [v for v in request.vehicles if v.available]
    stop_limit = max((v.max_stops for v in vehicles), default=1)

    arrivals = _earliest_arrivals(graph, buyer_ids, stop_limit)
    time_ok = set()
    for (bid, pid), order in orders.items():
        prod = products[product_index[pid]]
        if bid in arrivals and arrivals[bid] <= prod.max_delivery_hours:
            time_ok.add((bid, pid))

    if not vehicles or not time_ok:
        return _empty_response(request, arrivals)

    all_node_ids = [FARM] + buyer_ids
    feasible_edges = []
    for fi in all_node_ids:
        for to_id in buyer_ids:
            if fi == to_id or _hop(graph, fi, to_id) is None:
                continue
            if any((to_id, pid) in time_ok for pid in product_index):
                feasible_edges.append((fi, to_id))
    for bj in buyer_ids:
        if _hop(graph, bj, FARM) is None:
            continue
        if any((bj, pid) in time_ok for pid in product_index):
            feasible_edges.append((bj, FARM))

    if not feasible_edges:
        return _empty_response(request, arrivals)

    unload_sec_per_kg = int(round(request.unload_seconds_per_kg))
    max_capacity = max((int(v.capacity_kg) for v in vehicles), default=0)
    arrival_cap = max(
        (_hours_to_int(product.max_delivery_hours) for product in products),
        default=1,
    ) + unload_sec_per_kg * max_capacity

    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    if time_limit_seconds:
        solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_workers = 4

    # Edge variables: x[v,t,from,to]
    x = {}
    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            for fi, to_id in feasible_edges:
                x[(vi, ti, fi, to_id)] = model.NewBoolVar(
                    f"x_{vi}_{ti}_{fi}_{to_id}"
                )

    # Visit variables: y[v,t,buyer] - 1 if buyer is visited in trip t
    y = {}
    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            for bj in buyer_ids:
                y[vi, ti, bj] = model.NewBoolVar(f"y_{vi}_{ti}_{bj}")

    arr = {}
    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            for bj in buyer_ids:
                arr[vi, ti, bj] = model.NewIntVar(
                    0, arrival_cap, f"arr_{vi}_{ti}_{bj}"
                )

    # Cargo variables: z[v,t,buyer,product]
    z = {}
    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            for to_id in buyer_ids:
                for pi, prod in enumerate(products):
                    if (to_id, prod.id) not in time_ok:
                        continue
                    z[(vi, ti, to_id, pi)] = model.NewIntVar(
                        0, int(v.capacity_kg), f"z_{vi}_{ti}_{to_id}_{pi}"
                    )

    node_index = {FARM: 0}
    for offset, buyer_id in enumerate(buyer_ids, start=1):
        node_index[buyer_id] = offset

    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            arcs = []
            farm_skip = model.NewBoolVar(f"farm_skip_{vi}_{ti}")
            arcs.append((0, 0, farm_skip))
            for bj in buyer_ids:
                skip = model.NewBoolVar(f"skip_{vi}_{ti}_{bj}")
                arcs.append((node_index[bj], node_index[bj], skip))
                model.Add(skip + y[vi, ti, bj] == 1)
            for fi, to_id in feasible_edges:
                arcs.append(
                    (node_index[fi], node_index[to_id], x[(vi, ti, fi, to_id)])
                )
            model.AddCircuit(arcs)
            model.Add(sum(y[vi, ti, bj] for bj in buyer_ids) <= v.max_stops)

    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            for fi, to_id in feasible_edges:
                if to_id == FARM:
                    continue
                ev = x[(vi, ti, fi, to_id)]
                hop = _hop(graph, fi, to_id)
                hop_sec = _hours_to_int(hop[0])
                dest_arr = arr[vi, ti, to_id]
                load_here = [
                    z[(vi, ti, to_id, pi)]
                    for pi in range(len(products))
                    if (vi, ti, to_id, pi) in z
                ]
                unload = unload_sec_per_kg * sum(load_here) if load_here else 0
                if fi == FARM:
                    model.Add(dest_arr == hop_sec + unload).OnlyEnforceIf(ev)
                else:
                    model.Add(
                        dest_arr == arr[vi, ti, fi] + hop_sec + unload
                    ).OnlyEnforceIf(ev)

    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            for bj in buyer_ids:
                incoming = [
                    x[(vi, ti, fid, bj)]
                    for fid in all_node_ids
                    if (vi, ti, fid, bj) in x
                ]
                if incoming:
                    model.Add(y[vi, ti, bj] == sum(incoming))

    for key, var in z.items():
        vi, ti, bj, pi = key
        incoming = [
            x[(vi, ti, fid, bj)]
            for fid in all_node_ids
            if (vi, ti, fid, bj) in x
        ]
        cap = int(vehicles[vi].capacity_kg)
        if incoming:
            model.Add(var <= cap * sum(incoming))
        limit = _hours_to_int(products[pi].max_delivery_hours)
        late = model.NewBoolVar(f"late_{vi}_{ti}_{bj}_{pi}")
        model.Add(arr[vi, ti, bj] >= limit + 1).OnlyEnforceIf(late)
        model.Add(arr[vi, ti, bj] <= limit).OnlyEnforceIf(late.Not())
        model.Add(var == 0).OnlyEnforceIf(late)

    groups: dict[tuple, list[int]] = {}
    for vi, v in enumerate(vehicles):
        groups.setdefault(_vehicle_signature(v), []).append(vi)
    for indexes in groups.values():
        for left, right in zip(indexes, indexes[1:]):
            used_left = [
                x[key]
                for key in x
                if key[0] == left and key[2] == FARM and key[3] != FARM
            ]
            used_right = [
                x[key]
                for key in x
                if key[0] == right and key[2] == FARM and key[3] != FARM
            ]
            if used_left and used_right:
                model.Add(sum(used_left) >= sum(used_right))

    # 7. Load capacity per trip
    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            total = [
                z[(vi, ti, bj, pi)]
                for bj in buyer_ids
                for pi in range(len(products))
                if (bj, products[pi].id) in time_ok
            ]
            if total:
                model.Add(sum(total) <= int(v.capacity_kg))

    # 8. Stock
    for pi, prod in enumerate(products):
        total = [
            z[(vi, ti, bj, pi)]
            for vi, v in enumerate(vehicles)
            for ti in range(v.max_trips)
            for bj in buyer_ids
            if (bj, prod.id) in time_ok
        ]
        if total:
            model.Add(sum(total) <= int(prod.stock_kg))

    # 9. Demand
    for bj in buyer_ids:
        for pi, prod in enumerate(products):
            if (bj, prod.id) not in orders:
                continue
            demand = orders[(bj, prod.id)].demand_kg
            total = [
                z[(vi, ti, bj, pi)]
                for vi, v in enumerate(vehicles)
                for ti in range(v.max_trips)
                if (vi, ti, bj, pi) in z
            ]
            if total:
                model.Add(sum(total) <= int(demand))

    # --- Objective: maximize profit ---
    rev_terms = [
        int(round(orders[(bj, products[pi].id)].price_per_kg * 100))
        * z[(vi, ti, bj, pi)]
        for (vi, ti, bj, pi) in z
    ]
    cost_terms = [
        int(
            round(
                fuel_cost_rub(
                    _hop(graph, fi, tid)[1],
                    vehicles[vi].fuel_consumption_l_per_100km,
                    vehicles[vi].fuel_price_rub_per_liter,
                )
                * 100
            )
        )
        * x[(vi, ti, fi, tid)]
        for (vi, ti, fi, tid) in x
    ]
    model.Maximize(sum(rev_terms) - sum(cost_terms))

    # --- Solve ---
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        return _response_from_solver(
            request, SolverStatus.INFEASIBLE,
            "Для этих данных нет допустимого плана.", [], [], arrivals
        )
    plan_status, plan_message = _status_from_cpsat(status)
    if plan_status == SolverStatus.NOT_SOLVED:
        return _response_from_solver(
            request, plan_status, plan_message, [], [], arrivals
        )

    # --- Extract solution ---
    shipment_kg = {}
    trips_map = {}

    for key, var in z.items():
        if solver.Value(var) > LOAD_EPS:
            vi, ti, bj, pi = key
            k = (products[pi].id, bj, vehicles[vi].id)
            shipment_kg[k] = shipment_kg.get(k, 0.0) + solver.Value(var)

    for vi, v in enumerate(vehicles):
        for ti in range(v.max_trips):
            edges = [
                (fi, tid)
                for fi, tid in feasible_edges
                if solver.Value(x[(vi, ti, fi, tid)]) > 0.5
            ]
            if edges:
                trips_map[(v.id, ti)] = {"vi": vi, "edges": edges}

    buyers_by_id = {buyer.id: buyer for buyer in buyers}
    trips = []
    for (_vid, trip_idx), info in trips_map.items():
        vi = info["vi"]
        ti = trip_idx
        v = vehicles[vi]
        path = _path_from_farm(info["edges"])
        if not path:
            continue
        elapsed = 0.0
        distance_km = 0.0
        previous = FARM
        stops: list[Stop] = []
        for buyer_id in path:
            hours, km = _hop(graph, previous, buyer_id)
            elapsed += hours
            distance_km += km
            load_kg = 0.0
            for product_index, product in enumerate(products):
                var = z.get((vi, ti, buyer_id, product_index))
                if var is None:
                    continue
                load_kg += solver.Value(var)
            elapsed += unload_sec_per_kg * load_kg / HOUR_SECONDS
            stops.append(
                Stop(
                    buyer_id=buyer_id,
                    arrival_hours=round(elapsed, 2),
                    load_kg=round(load_kg, 3),
                )
            )
            previous = buyer_id
        back = _hop(graph, path[-1], FARM)
        if back is not None:
            distance_km += back[1]
        total_load = sum(stop.load_kg for stop in stops)
        if total_load < LOAD_EPS:
            continue
        waypoints = [
            {"id": FARM, "longitude": request.farm.longitude, "latitude": request.farm.latitude}
        ]
        for buyer_id in path:
            buyer = buyers_by_id[buyer_id]
            waypoints.append(
                {"id": buyer.id, "longitude": buyer.longitude, "latitude": buyer.latitude}
            )
        waypoints.append(
            {"id": FARM, "longitude": request.farm.longitude, "latitude": request.farm.latitude}
        )
        trips.append(
            Trip(
                vehicle_id=v.id,
                stops=stops,
                distance_km=round(distance_km, 2),
                cost=round(
                    fuel_cost_rub(
                        distance_km,
                        v.fuel_consumption_l_per_100km,
                        v.fuel_price_rub_per_liter,
                    ),
                    2,
                ),
                load_kg=round(total_load, 3),
                waypoints=waypoints,
                geometry={
                    "type": "LineString",
                    "coordinates": [
                        [point["longitude"], point["latitude"]] for point in waypoints
                    ],
                },
            )
        )

    shipments = [
        Shipment(product_id=pid, buyer_id=bid, vehicle_id=vid,
                 quantity_kg=round(amt, 3))
        for (pid, bid, vid), amt in sorted(shipment_kg.items())
        if amt >= LOAD_EPS
    ]

    return _response_from_solver(
        request, plan_status, plan_message, shipments, trips, arrivals
    )


def _status_from_cpsat(status: int) -> tuple[SolverStatus, str]:
    """OPTIMAL только если CP-SAT доказал оптимум. FEASIBLE — есть план, доказательств нет."""
    if status == cp_model.OPTIMAL:
        return SolverStatus.OPTIMAL, "План рассчитан по данным запроса."
    if status == cp_model.FEASIBLE:
        return (
            SolverStatus.FEASIBLE,
            "Найден допустимый план. За отведённое время оптимум не доказан.",
        )
    return SolverStatus.NOT_SOLVED, "Решатель не нашёл план."


def _path_from_farm(edges: list[tuple[str, str]]) -> list[str]:
    """Покупатели выезда по порядку, начиная с ребра из farm."""
    outgoing = {origin: dest for origin, dest in edges}
    path: list[str] = []
    node = FARM
    seen: set[str] = set()
    while node in outgoing:
        nxt = outgoing[node]
        if nxt == FARM:
            break
        if nxt in seen:
            break
        seen.add(nxt)
        path.append(nxt)
        node = nxt
    return path


def _earliest_arrivals(graph, buyer_ids, max_stops):
    """Минимальное время до покупателя за не больше max_stops рёбер."""
    best: dict[str, float] = {}
    layer: dict[str, float] = {FARM: 0.0}
    for _layer in range(max_stops):
        nxt: dict[str, float] = {}
        for origin, elapsed in layer.items():
            for dest in buyer_ids:
                if origin == dest:
                    continue
                hop = _hop(graph, origin, dest)
                if hop is None:
                    continue
                candidate = elapsed + hop[0]
                current = nxt.get(dest)
                if current is None or candidate < current:
                    nxt[dest] = candidate
                known = best.get(dest)
                if known is None or candidate < known:
                    best[dest] = candidate
        layer = nxt
        if not layer:
            break
    return best


def _empty_response(request, arrivals):
    return _response_from_solver(
        request, SolverStatus.OPTIMAL,
        "По этим данным отгружать нечего: нет доступных машин или ни одна культура не успевает до покупателей.",
        [], [], arrivals
    )


def _response_from_solver(request, status, message, shipments, trips, arrivals):
    orders = {
        (b.id, o.product_id): o
        for b in request.buyers
        for o in b.orders
    }
    revenue = 0.0
    shipped_by_product = {}
    for s in shipments:
        revenue += s.quantity_kg * orders[(s.buyer_id, s.product_id)].price_per_kg
        shipped_by_product[s.product_id] = (
            shipped_by_product.get(s.product_id, 0) + s.quantity_kg
        )
    transport_cost = sum(t.cost for t in trips)
    balances = []
    for product in request.products:
        eligible_demand = 0.0
        for buyer in request.buyers:
            order = orders.get((buyer.id, product.id))
            arrived = arrivals.get(buyer.id)
            if order is None or arrived is None or arrived > product.max_delivery_hours:
                continue
            eligible_demand += order.demand_kg
        shipped = shipped_by_product.get(product.id, 0.0)
        balances.append(
            ProductBalance(product_id=product.id, stock_kg=product.stock_kg,
                shipped_kg=round(shipped, 3),
                leftover_kg=round(product.stock_kg - shipped, 3),
                loss_kg=round(max(0.0, product.stock_kg - eligible_demand), 3))
        )
    return PlanResponse(status=status, objective=OBJECTIVE, message=message,
        assumptions=ASSUMPTIONS, shipments=shipments, trips=trips,
        revenue=round(revenue, 2), transport_cost=round(transport_cost, 2),
        profit=round(revenue - transport_cost, 2), balances=balances)
