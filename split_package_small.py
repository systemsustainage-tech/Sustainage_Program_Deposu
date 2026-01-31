import os

# Source file
source_file = 'deploy_package.tar.gz'
# Chunk size (5MB)
chunk_size = 5 * 1024 * 1024

def split_file():
    if not os.path.exists(source_file):
        print(f"Error: {source_file} not found.")
        return

    file_size = os.path.getsize(source_file)
    print(f"Splitting {source_file} ({file_size} bytes) into {chunk_size} byte chunks...")

    part_num = 0
    with open(source_file, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            part_filename = f"deploy_package_small.part{part_num:03d}"
            with open(part_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)
            
            print(f"Created {part_filename} ({len(chunk)} bytes)")
            part_num += 1
    
    print(f"Done. Created {part_num} parts.")

if __name__ == "__main__":
    split_file()
