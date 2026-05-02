"""Simple demo launcher for 2D physics systems."""

from __future__ import annotations

from importlib import import_module
import sys


DEMO_MODULES = {
    "particle": "demos.particle_demo",
    "spring": "demos.spring_demo",
    "softbody": "demos.softbody_demo",
    "rigidbody": "demos.rigidbody_demo",
    "rigidbody_cube": "demos.rigidbody_cube_demo",
}


def launch_demo(name: str) -> None:
    module_path = DEMO_MODULES.get(name)
    if module_path is None:
        available = ", ".join(sorted(DEMO_MODULES))
        raise SystemExit(f"Unknown demo '{name}'. Available demos: {available}")

    module = import_module(module_path)
    module.run()


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)

    if args and args[0] in {"-h", "--help", "help"}:
        available = ", ".join(sorted(DEMO_MODULES))
        print(f"Usage: python main.py [demo]\nAvailable demos: {available}")
        return

    demo_name = args[0] if args else "spring"
    launch_demo(demo_name)


if __name__ == "__main__":
    main()
