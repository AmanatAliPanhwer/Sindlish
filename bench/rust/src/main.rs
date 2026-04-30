use std::env;

fn fib(n: u64) -> u64 {
    if n < 2 { return n; }
    fib(n - 1) + fib(n - 2)
}

fn is_prime(n: u64) -> bool {
    if n < 2 { return false; }
    let mut i = 2;
    while i * i <= n {
        if n % i == 0 { return false; }
        i += 1;
    }
    true
}

fn run_fib(n: u64) {
    println!("{}", fib(n));
}

fn run_loop() {
    let mut total: u64 = 0;
    for i in 0..100_000 {
        total += i;
    }
    println!("{}", total);
}

fn run_primes() {
    let mut count = 0;
    for i in 0..5_000 {
        if is_prime(i) {
            count += 1;
        }
    }
    println!("{}", count);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 { return; }

    match args[1].as_str() {
        "fib" => {
            let n = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(30);
            run_fib(n);
        }
        "loop" => run_loop(),
        "primes" => run_primes(),
        _ => {}
    }
}
