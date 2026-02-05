"""
Ray sanity check: init, one remote task, ray.get(), shutdown.
Run with: python -m image_ray.ray_check
"""

import ray


@ray.remote
def hello_ray():
    """Simple remote task to verify Ray workers run."""
    return "Ray is working!"


def main():
    print("Initializing Ray...")
    ray.init(ignore_reinit_error=True)
    try:
        ref = hello_ray.remote()
        result = ray.get(ref)
        print(f"Remote task returned: {result}")
    finally:
        ray.shutdown()
    print("Ray check complete.")


if __name__ == "__main__":
    main()
