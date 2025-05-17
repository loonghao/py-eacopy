use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use std::fs;
use std::io::Write;
use std::path::Path;
use tempfile::tempdir;

// Import the Rust implementation
use py_eacopy::{copy, copy2, copyfile, copytree, EACopy};

// Create a file with the specified size
fn create_test_file(path: &Path, size: usize) -> std::io::Result<()> {
    let mut file = fs::File::create(path)?;
    let data = vec![b'A'; 4096]; // 4KB chunk
    
    let mut remaining = size;
    while remaining > 0 {
        let chunk_size = std::cmp::min(remaining, data.len());
        file.write_all(&data[..chunk_size])?;
        remaining -= chunk_size;
    }
    
    Ok(())
}

// Create a directory structure with the specified number of files and size
fn create_test_directory(dir: &Path, num_files: usize, file_size: usize) -> std::io::Result<()> {
    fs::create_dir_all(dir)?;
    
    for i in 0..num_files {
        let file_path = dir.join(format!("file_{}.txt", i));
        create_test_file(&file_path, file_size)?;
    }
    
    // Create a subdirectory with a few files
    let subdir = dir.join("subdir");
    fs::create_dir_all(&subdir)?;
    
    for i in 0..3 {
        let file_path = subdir.join(format!("subfile_{}.txt", i));
        create_test_file(&file_path, file_size / 2)?;
    }
    
    Ok(())
}

// Benchmark copyfile function
fn bench_copyfile(c: &mut Criterion) {
    let mut group = c.benchmark_group("copyfile");
    
    // Test with different file sizes
    for size in [1024, 1024 * 1024, 10 * 1024 * 1024].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(size), size, |b, &size| {
            b.iter_with_setup(
                || {
                    // Setup: Create a temporary directory and a test file
                    let temp_dir = tempdir().unwrap();
                    let source_path = temp_dir.path().join("source.txt");
                    let dest_path = temp_dir.path().join("dest.txt");
                    create_test_file(&source_path, size).unwrap();
                    (temp_dir, source_path, dest_path)
                },
                |(temp_dir, source_path, dest_path)| {
                    // Benchmark: Copy the file
                    black_box(copyfile(&source_path, &dest_path).unwrap());
                    // Cleanup is handled by temp_dir's Drop implementation
                },
            );
        });
    }
    
    group.finish();
}

// Benchmark copy function
fn bench_copy(c: &mut Criterion) {
    let mut group = c.benchmark_group("copy");
    
    // Test with different file sizes
    for size in [1024, 1024 * 1024, 10 * 1024 * 1024].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(size), size, |b, &size| {
            b.iter_with_setup(
                || {
                    // Setup: Create a temporary directory and a test file
                    let temp_dir = tempdir().unwrap();
                    let source_path = temp_dir.path().join("source.txt");
                    let dest_path = temp_dir.path().join("dest.txt");
                    create_test_file(&source_path, size).unwrap();
                    (temp_dir, source_path, dest_path)
                },
                |(temp_dir, source_path, dest_path)| {
                    // Benchmark: Copy the file
                    black_box(copy(&source_path, &dest_path).unwrap());
                    // Cleanup is handled by temp_dir's Drop implementation
                },
            );
        });
    }
    
    group.finish();
}

// Benchmark copy2 function
fn bench_copy2(c: &mut Criterion) {
    let mut group = c.benchmark_group("copy2");
    
    // Test with different file sizes
    for size in [1024, 1024 * 1024, 10 * 1024 * 1024].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(size), size, |b, &size| {
            b.iter_with_setup(
                || {
                    // Setup: Create a temporary directory and a test file
                    let temp_dir = tempdir().unwrap();
                    let source_path = temp_dir.path().join("source.txt");
                    let dest_path = temp_dir.path().join("dest.txt");
                    create_test_file(&source_path, size).unwrap();
                    (temp_dir, source_path, dest_path)
                },
                |(temp_dir, source_path, dest_path)| {
                    // Benchmark: Copy the file with metadata
                    black_box(copy2(&source_path, &dest_path).unwrap());
                    // Cleanup is handled by temp_dir's Drop implementation
                },
            );
        });
    }
    
    group.finish();
}

// Benchmark copytree function
fn bench_copytree(c: &mut Criterion) {
    let mut group = c.benchmark_group("copytree");
    
    // Test with different numbers of files
    for num_files in [10, 50, 100].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(num_files), num_files, |b, &num_files| {
            b.iter_with_setup(
                || {
                    // Setup: Create a temporary directory and a test directory structure
                    let temp_dir = tempdir().unwrap();
                    let source_dir = temp_dir.path().join("source");
                    let dest_dir = temp_dir.path().join("dest");
                    create_test_directory(&source_dir, num_files, 1024).unwrap();
                    (temp_dir, source_dir, dest_dir)
                },
                |(temp_dir, source_dir, dest_dir)| {
                    // Benchmark: Copy the directory tree
                    black_box(copytree(&source_dir, &dest_dir, false, false, false).unwrap());
                    // Cleanup is handled by temp_dir's Drop implementation
                },
            );
        });
    }
    
    group.finish();
}

// Benchmark EACopy class
fn bench_eacopy_class(c: &mut Criterion) {
    let mut group = c.benchmark_group("EACopy");
    
    // Test with different file sizes
    for size in [1024, 1024 * 1024, 10 * 1024 * 1024].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(size), size, |b, &size| {
            b.iter_with_setup(
                || {
                    // Setup: Create a temporary directory and a test file
                    let temp_dir = tempdir().unwrap();
                    let source_path = temp_dir.path().join("source.txt");
                    let dest_path = temp_dir.path().join("dest.txt");
                    create_test_file(&source_path, size).unwrap();
                    (temp_dir, source_path, dest_path)
                },
                |(temp_dir, source_path, dest_path)| {
                    // Benchmark: Create an EACopy instance and copy the file
                    let eacopy = EACopy::new();
                    black_box(eacopy.copy(&source_path, &dest_path).unwrap());
                    // Cleanup is handled by temp_dir's Drop implementation
                },
            );
        });
    }
    
    group.finish();
}

criterion_group!(
    benches,
    bench_copyfile,
    bench_copy,
    bench_copy2,
    bench_copytree,
    bench_eacopy_class
);
criterion_main!(benches);
