"""
Verification script to test Live Mode and Simulation Mode isolation
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def get_live_stats():
    """Get Live Mode stats"""
    response = requests.get(f"{BASE_URL}/api/stats")
    return response.json()

def get_simulation_stats():
    """Get Simulation Mode stats"""
    response = requests.get(f"{BASE_URL}/simulation/stats")
    return response.json()

def test_live_mode():
    """Test that Live Mode only counts real endpoint hits"""
    print_section("TEST 1: Live Mode Request Counting")
    
    # Get initial stats
    initial_stats = get_live_stats()
    initial_count = initial_stats['total_api_calls']
    print(f"Initial Live Mode count: {initial_count}")
    
    # Hit a real endpoint via Swagger UI simulation
    print("\nHitting /login endpoint (should count)...")
    requests.post(f"{BASE_URL}/login", json={"username": "test", "password": "test"})
    time.sleep(0.5)
    
    # Check stats endpoint (should NOT count)
    print("Hitting /api/stats endpoint (should NOT count)...")
    requests.get(f"{BASE_URL}/api/stats")
    time.sleep(0.5)
    
    # Get final stats
    final_stats = get_live_stats()
    final_count = final_stats['total_api_calls']
    print(f"\nFinal Live Mode count: {final_count}")
    print(f"Increase: {final_count - initial_count}")
    
    if final_count - initial_count == 1:
        print("✓ PASS: Only /login counted, /api/stats ignored")
        return True
    else:
        print("✗ FAIL: Incorrect count increase")
        return False

def test_simulation_isolation():
    """Test that Simulation Mode doesn't affect Live Mode"""
    print_section("TEST 2: Simulation Mode Isolation")
    
    # Get initial live stats
    initial_live = get_live_stats()
    initial_live_count = initial_live['total_api_calls']
    print(f"Initial Live Mode count: {initial_live_count}")
    
    # Start simulation
    print("\nStarting simulation for /payment endpoint...")
    sim_response = requests.post(
        f"{BASE_URL}/simulation/start",
        params={
            "simulated_endpoint": "/payment",
            "duration_seconds": 5,
            "requests_per_window": 20
        }
    )
    print(f"Simulation started: {sim_response.json()}")
    
    # Wait for simulation to generate traffic
    time.sleep(6)
    
    # Get simulation stats
    sim_stats = get_simulation_stats()
    print(f"\nSimulation stats:")
    print(f"  - Total requests: {sim_stats['total_requests']}")
    print(f"  - Active: {sim_stats['active']}")
    
    # Get final live stats
    final_live = get_live_stats()
    final_live_count = final_live['total_api_calls']
    print(f"\nFinal Live Mode count: {final_live_count}")
    print(f"Live Mode increase: {final_live_count - initial_live_count}")
    
    if final_live_count == initial_live_count:
        print("✓ PASS: Simulation traffic did NOT affect Live Mode")
        return True
    else:
        print("✗ FAIL: Simulation traffic leaked into Live Mode")
        return False

def test_simulation_reset():
    """Test that simulation state resets properly"""
    print_section("TEST 3: Simulation State Reset")
    
    # Start first simulation
    print("Starting first simulation...")
    requests.post(
        f"{BASE_URL}/simulation/start",
        params={
            "simulated_endpoint": "/login",
            "duration_seconds": 3,
            "requests_per_window": 10
        }
    )
    time.sleep(4)
    
    # Stop simulation
    print("Stopping simulation...")
    stop_response = requests.post(f"{BASE_URL}/simulation/stop")
    print(f"Stop response: {stop_response.json()}")
    
    # Check stats after stop
    stats_after_stop = get_simulation_stats()
    print(f"\nStats after stop:")
    print(f"  - Active: {stats_after_stop['active']}")
    print(f"  - Total requests: {stats_after_stop['total_requests']}")
    
    # Start second simulation
    print("\nStarting second simulation...")
    requests.post(
        f"{BASE_URL}/simulation/start",
        params={
            "simulated_endpoint": "/search",
            "duration_seconds": 3,
            "requests_per_window": 10
        }
    )
    time.sleep(1)
    
    # Check stats during second run
    stats_second_run = get_simulation_stats()
    print(f"\nStats during second run:")
    print(f"  - Active: {stats_second_run['active']}")
    print(f"  - Total requests: {stats_second_run['total_requests']}")
    print(f"  - Simulated endpoint: {stats_second_run['simulated_endpoint']}")
    
    # Stop second simulation
    time.sleep(3)
    requests.post(f"{BASE_URL}/simulation/stop")
    
    if stats_second_run['simulated_endpoint'] == '/search' and stats_second_run['total_requests'] < 50:
        print("✓ PASS: Simulation state reset properly between runs")
        return True
    else:
        print("✗ FAIL: Simulation state not reset properly")
        return False

def test_database_isolation():
    """Test that database queries filter correctly"""
    print_section("TEST 4: Database Query Isolation")
    
    # Get live logs
    live_logs_response = requests.get(f"{BASE_URL}/api/logs?limit=10")
    live_logs = live_logs_response.json()
    
    # Get simulation anomaly history
    sim_history_response = requests.get(f"{BASE_URL}/simulation/anomaly-history?limit=10")
    sim_history = sim_history_response.json()
    
    print(f"Live logs count: {len(live_logs)}")
    print(f"Simulation history count: {len(sim_history)}")
    
    # Check that live logs don't have is_simulation=True
    live_has_sim = any(log.get('is_simulation', False) for log in live_logs)
    
    # Check that simulation history only has is_simulation=True
    sim_all_marked = all(log.get('is_simulation', False) for log in sim_history) if sim_history else True
    
    if not live_has_sim and sim_all_marked:
        print("✓ PASS: Database queries properly isolated")
        return True
    else:
        print("✗ FAIL: Database queries not properly isolated")
        return False

def run_all_tests():
    """Run all isolation tests"""
    print_section("ISOLATION VERIFICATION TESTS")
    
    results = []
    
    try:
        results.append(("Live Mode Counting", test_live_mode()))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        results.append(("Live Mode Counting", False))
    
    time.sleep(2)
    
    try:
        results.append(("Simulation Isolation", test_simulation_isolation()))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        results.append(("Simulation Isolation", False))
    
    time.sleep(2)
    
    try:
        results.append(("Simulation Reset", test_simulation_reset()))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        results.append(("Simulation Reset", False))
    
    time.sleep(2)
    
    try:
        results.append(("Database Isolation", test_database_isolation()))
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        results.append(("Database Isolation", False))
    
    # Print summary
    print_section("TEST SUMMARY")
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    return all(passed for _, passed in results)

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
