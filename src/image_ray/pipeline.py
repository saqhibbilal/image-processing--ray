"""
Phase 2: Parallel batch processing pipeline using Ray.

Chunks image paths, assigns each chunk to a Ray worker, aggregates results.
"""

import math
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import ray

from image_ray import image_ops


def discover_images(directory: Path, extensions: List[str] = None) -> List[Path]:
    """
    Find all image files in a directory.

    Args:
        directory: Directory to search.
        extensions: List of extensions (e.g. ['.png', '.jpg']). Default: common image formats.

    Returns:
        List of image file paths.
    """
    if extensions is None:
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    directory = Path(directory)
    if not directory.is_dir():
        return []
    images = []
    for ext in extensions:
        images.extend(directory.glob(f'*{ext}'))
        images.extend(directory.glob(f'*{ext.upper()}'))
    return sorted(images)


def chunk_paths(paths: List[Path], num_chunks: int) -> List[List[Path]]:
    """
    Split a list of paths into approximately equal chunks.

    Args:
        paths: List of file paths.
        num_chunks: Number of chunks to create.

    Returns:
        List of chunks, each chunk is a list of paths.
    """
    if not paths:
        return []
    if num_chunks <= 0:
        num_chunks = 1
    if num_chunks >= len(paths):
        return [[p] for p in paths]

    chunk_size = math.ceil(len(paths) / num_chunks)
    chunks = []
    for i in range(0, len(paths), chunk_size):
        chunks.append(paths[i:i + chunk_size])
    return chunks


@ray.remote
def process_chunk(chunk_paths: List[Path], ops: Dict[str, Any], output_dir: Path = None) -> Dict[str, Any]:
    """
    Process a chunk of images. Runs in a Ray worker.

    Args:
        chunk_paths: List of input image paths for this chunk.
        ops: Operations dict (same format as image_ops.process_image).
        output_dir: Optional output directory. If None, overwrites originals.

    Returns:
        Dict with 'processed': count, 'failed': list of (path, error) tuples.
    """
    processed = 0
    failed = []

    for path_in in chunk_paths:
        try:
            if output_dir:
                # Preserve relative structure or flatten to output_dir
                path_out = output_dir / path_in.name
            else:
                path_out = path_in  # Overwrite

            image_ops.process_image(path_in, path_out, ops)
            processed += 1
        except Exception as e:
            failed.append((str(path_in), str(e)))

    return {
        'processed': processed,
        'failed': failed
    }


def run_pipeline(
    input_dir: Path,
    ops: Dict[str, Any],
    output_dir: Path = None,
    num_chunks: int = None
) -> Dict[str, Any]:
    """
    Main pipeline: discover images, chunk, process in parallel with Ray, aggregate.

    Args:
        input_dir: Directory containing input images.
        ops: Operations dict for image_ops.process_image.
        output_dir: Optional output directory. If None, overwrites originals.
        num_chunks: Number of chunks (default: number of CPU cores).

    Returns:
        Dict with 'total_processed', 'total_failed', 'failed_paths', 'duration_seconds'.
    """
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Discover images
    print(f"Discovering images in {input_dir}...")
    image_paths = discover_images(input_dir)
    if not image_paths:
        return {
            'total_processed': 0,
            'total_failed': 0,
            'failed_paths': [],
            'duration_seconds': 0.0
        }
    print(f"Found {len(image_paths)} images")

    # Determine number of chunks
    if num_chunks is None:
        import os
        num_chunks = max(1, os.cpu_count() or 1)
    num_chunks = min(num_chunks, len(image_paths))  # Don't create more chunks than images

    # Chunk paths
    chunks = chunk_paths(image_paths, num_chunks)
    print(f"Split into {len(chunks)} chunks (target: {num_chunks} chunks)")

    # Initialize Ray if not already initialized
    try:
        ray.init(ignore_reinit_error=True)
    except Exception:
        pass  # Already initialized

    # Submit tasks
    print(f"Submitting {len(chunks)} tasks to Ray workers...")
    start_time = time.time()
    refs = [process_chunk.remote(chunk, ops, output_dir) for chunk in chunks]
    results = ray.get(refs)
    duration = time.time() - start_time

    # Aggregate results
    total_processed = sum(r['processed'] for r in results)
    total_failed = sum(len(r['failed']) for r in results)
    failed_paths = []
    for r in results:
        failed_paths.extend(r['failed'])

    return {
        'total_processed': total_processed,
        'total_failed': total_failed,
        'failed_paths': failed_paths,
        'duration_seconds': duration
    }
