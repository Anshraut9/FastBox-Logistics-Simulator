import json
import math
import csv
from typing import Dict, List, Tuple

def calculate_distance(point1: List[float], point2: List[float]) -> float:
    """Calculates Euclidean distance between two [x, y] coordinates."""
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def load_data(filepath: str) -> Dict:
    with open(filepath, 'r') as file:
        return json.load(file)

def simulate_logistics(data: Dict) -> Dict:

    """
    Simulates the delivery process.
    
    ASSUMPTION DOCUMENTATION (per assignment instructions):
    1. Dynamic Routing: Agents update their 'current_loc' to the package destination 
       after each delivery. Subsequent warehouse distances are calculated from this new location.
    2. Sample Output Discrepancy: The mathematical execution of the provided coordinates 
       results in A2 being the most efficient agent (Total Dist: ~79.21, Efficiency: ~39.6). 
       The script prioritizes accurate Euclidean calculations over matching the arbitrary 
       dummy values (e.g., A1 = 85.32) in the prompt's sample report.
    """
    warehouses = data['warehouses']
    agents = data['agents']
    packages = data['packages']
    
    # Initialize agent tracking metrics
    agent_stats = {
        agent_id: {"packages_delivered": 0, "total_distance": 0.0, "current_loc": loc}
        for agent_id, loc in agents.items()
    }
    
    for pkg in packages:
        warehouse_loc = warehouses[pkg['warehouse']]
        dest_loc = pkg['destination']
        
        # 1. Assign to nearest agent based on agent's current location to warehouse
        best_agent = None
        min_distance = float('inf')
        
        for agent_id, stats in agent_stats.items():
            dist_to_wh = calculate_distance(stats["current_loc"], warehouse_loc)
            if dist_to_wh < min_distance:
                min_distance = dist_to_wh
                best_agent = agent_id
                
        # 2. Simulate Delivery Sequence: Agent -> Warehouse -> Destination
        agent = agent_stats[best_agent]
        dist_to_wh = calculate_distance(agent["current_loc"], warehouse_loc)
        dist_wh_to_dest = calculate_distance(warehouse_loc, dest_loc)
        
        # 3. Update agent metrics
        route_distance = dist_to_wh + dist_wh_to_dest
        agent["total_distance"] += route_distance
        agent["packages_delivered"] += 1
        agent["current_loc"] = dest_loc # Agent stays at destination after delivery
        
    # 4. Generate Final Report Metrics
    report = {}
    top_performer = None
    max_efficiency_score = float('-inf') # Lower distance per package is better, but we match sample format
    
    for agent_id, stats in agent_stats.items():
        pkgs = stats["packages_delivered"]
        dist = stats["total_distance"]
        
        if pkgs > 0:
            efficiency = round(dist / pkgs, 2)
        else:
            efficiency = 0.0
            
        report[agent_id] = {
            "packages_delivered": pkgs,
            "total_distance": round(dist, 2),
            "efficiency": efficiency
        }
        
        # Determine best agent (highest deliveries, tie-breaker: best efficiency)
        score = pkgs * 1000 - efficiency 
        if score > max_efficiency_score:
            max_efficiency_score = score
            top_performer = agent_id
            
    report["best_agent"] = top_performer
    return report

def export_results(report: Dict):
    """Saves to JSON and exports top performer to CSV (Bonus Task)."""
    with open('report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    best_agent_id = report["best_agent"]
    best_stats = report[best_agent_id]
    
    with open('top_performer.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Agent_ID", "Packages_Delivered", "Total_Distance", "Efficiency"])
        writer.writerow([best_agent_id, best_stats["packages_delivered"], 
                         best_stats["total_distance"], best_stats["efficiency"]])

if __name__ == "__main__":
    # Execution Flow
    raw_data = load_data('data.json')
    final_report = simulate_logistics(raw_data)
    export_results(final_report)
    print("Simulation complete. 'report.json' and 'top_performer.csv' generated successfully.")