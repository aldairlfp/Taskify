"""
Simple Test Runner
Easy way to run the simplified tests
"""

import subprocess
import sys


def run_simple_tests():
    """Run all simple tests"""
    print("🧪 Running Simple Taskify Tests")
    print("=" * 40)

    # Test commands to run
    test_commands = [
        ("pytest tests/simple_test_api.py -v", "API Tests"),
        ("pytest tests/simple_test_core.py -v", "Core Tests"),
        ("pytest tests/simple_test_auth.py -v", "Auth Tests"),
        ("pytest tests/simple_test_tasks.py -v", "Task Tests"),
    ]

    results = []

    for command, name in test_commands:
        print(f"\n🚀 Running {name}...")
        print("-" * 30)

        try:
            result = subprocess.run(command, shell=True, check=True)
            results.append((name, True))
            print(f"✅ {name} PASSED")
        except subprocess.CalledProcessError:
            results.append((name, False))
            print(f"❌ {name} FAILED")

    # Summary
    print(f"\n📊 Summary")
    print("=" * 40)
    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")

    print(f"\nResult: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 All simple tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_simple_tests())
