from typing import Callable
import numpy as np
from matplotlib import pyplot as plt

def rde_implicit_solver(N: int, l: float, alpha: Callable[[float], float]) -> list[np.ndarray]:
    from tqdm import tqdm
    """
    Implicitly solve the ODE system using the implicit Euler method.
    """
    inv_l = 1 / l
    h = 1 / N

    def get_t_n(n: int) -> float:
        return n * h

    y = np.empty((3, N+1), dtype=float)
    y[:, N] = (1, 0, 0) # initial condition
    # integrate backwards
    for n in tqdm(range(N-1, -1, -1), desc="integrating ...", unit="step"):
        # implicit Euler step
        a_n, b_n, c_n = y[:, n+1]
        t_n = get_t_n(n)

        a_n_1 = a_n - h * (inv_l * b_n**2)
        b_n_1 = (b_n + h * a_n) / (1 + h * (alpha(t_n) + inv_l * c_n))

        # solve for c_n_1
        A = h * inv_l
        B = 1 + 2 * h * alpha(t_n) # always nonnegative
        C = - c_n - 2 * h * b_n
        D = B ** 2 - 4 * A * C
        c_n_1 = (- B + np.sqrt(D)) / (2 * A) # we want the positive root

        y[:, n] = (a_n_1, b_n_1, c_n_1)

    t = np.array([get_t_n(n) for n in range(N+1)])
    a, b, c = y[0, :], y[1, :], y[2, :]
    return t, a, b, c

def rde_scipy_solver(N: int, l: float, alpha: Callable[[float], float]) -> list[np.ndarray]:
    from scipy.integrate import solve_ivp
    """
    Solve the ODE system using scipy"s solve_ivp.
    """
    def f(t: float, y: np.ndarray) -> np.ndarray:
        inv_l = 1 / l
        a, b, c = y
        a_dot = inv_l * b**2
        b_dot = -a + b * alpha(t) + inv_l * b * c
        c_dot = - 2 * b + 2 * c * alpha(t) - inv_l * c**2
        return np.array([a_dot, b_dot, c_dot])
    
    sol = solve_ivp(
        fun=f,
        y0=np.array([1, 0, 0]),
        t_span=[1, 0],
        t_eval=np.linspace(1, 0, N),
        method="LSODA",  # stiff solver
    )

    if not sol.success:
        raise ValueError(sol.message)


    t, y = sol.t, sol.y
    a, b, c = y[0, :], y[1, :], y[2, :]
    return t, a, b, c

def hjb_shooting_solver(N: int, l: float, alpha: Callable[[float], float]) -> list[np.ndarray]:
    """
    Solve the HJB equation using the shooting method.
    """
    from scipy.integrate import solve_ivp
    from scipy.optimize import root
    def g(t: float, y: np.ndarray) -> np.ndarray:
        x, v, p, q = y
        u = q / (2 * l) 

        x_dot = v
        v_dot = -alpha(t) * v + u
        p_dot = 0
        q_dot = p - alpha(t) * q
        return np.array([x_dot, v_dot, p_dot, q_dot])

    def f(z: np.ndarray) -> float:
        p_0, q_0 = z
        x_0, v_0 = 1, 0

        sol = solve_ivp(
            fun=g,
            y0=np.array([x_0, v_0, p_0, q_0]),
            t_span=[0, 1],
            t_eval=np.linspace(0, 1, N),
            method="LSODA", # stiff solver
        )
        
        if not sol.success:
            raise ValueError(sol.message)
        
        x_1, v_1, p_1, q_1 = sol.y[:, -1]
        return np.array([p_1 - 2 * x_1, q_1]), sol.t, sol.y

    p_0, q_0 = 0, 0 # initial guess for p, q
    sol = root(
        fun=lambda z: f(z)[0],
        x0=np.array([p_0, q_0]),
        method="hybr", # default solver in scipy
    )
    if not sol.success:
        raise ValueError(sol.message)
    p_0, q_0 = sol.x
    # Re-run the ODE with the found p_0, q_0
    _, t, y = f(np.array([p_0, q_0]))
    x, v, p, q = y

    return t, x, v, p, q

def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--l", type=float, default=1.0, help="Lambda value")
    parser.add_argument("--N", type=int, default=1000, help="Number of steps")
    parser.add_argument("--method", type=str, default="rde_implicit", choices=["rde_implicit", "rde_scipy", "hjb_shooting"], help="method to use")
    parser.add_argument("--alpha", type=str, default="sin10t", choices=["sin10t", "tsquare"], help="function to use for alpha")
    return parser.parse_args()

args = get_args()
l = args.l
N = args.N
if l <= 0:
    raise ValueError("l must be positive")
if N <= 0:
    raise ValueError("N must be positive")
if N < 2:
    raise ValueError("N must be at least 2")

solver = {
    "rde_implicit": rde_implicit_solver,
    "rde_scipy": rde_scipy_solver,
    "hjb_shooting": hjb_shooting_solver,
}[args.method]

if args.alpha == "sin10t":
    alpha = lambda t: float(np.sin(10 * t))
elif args.alpha == "tsquare":
    alpha = lambda t: t**2
else:
    raise ValueError("Invalid alpha function")


if args.method in ["rde_implicit", "rde_scipy"]:
    t, a, b, c = solver(
        N=N,
        l=l,
        alpha=alpha,
    )

    sort = np.argsort(t)
    t = t[sort]
    a = a[sort]
    b = b[sort]
    c = c[sort]

    print("optimal cost:", a[0])


    plt.plot(t, a, label="a")
    plt.plot(t, b, label="b")
    plt.plot(t, c, label="c")
    plt.legend()
    plt.xlabel("t")
    plt.ylabel("a,b,c")
    plt.title(f"lambda = {l} N = {N} alpha = {args.alpha} using {args.method} \n optimal cost = {a[0]:.6f}")
    plt.grid()
    plt.show()

if args.method in ["hjb_shooting"]:
    t, x, v, p, q = solver(
        N=N,
        l=l,
        alpha=alpha,
    )
    u = q / (2 * l)
    J = x[-1]**2 + np.trapezoid(l * u**2, t)
    print("optimal cost:", J)
    plt.plot(t, x, label="x")
    plt.plot(t, v, label="v")
    plt.plot(t, p, label="p")
    plt.plot(t, q, label="q")
    plt.legend()
    plt.xlabel("t")
    plt.ylabel("x,v,p,q")
    plt.title(f"lambda = {l} N = {N} alpha = {args.alpha} using {args.method} \n optimal cost = {J:.6f}")
    plt.grid()
    plt.show()

