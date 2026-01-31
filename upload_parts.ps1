$ErrorActionPreference = "Stop"
$key = "C:\Users\admin2\.ssh\id_ed25519"
$remote = "root@72.62.150.207"
$remote_path = "/var/www/sustainage/"

# Clean remote
# Write-Host "Cleaning remote..."
# ssh -i $key -o StrictHostKeyChecking=no $remote "rm -f $remote_path/deploy_package_small.part*"

# Upload parts
$parts = Get-ChildItem "deploy_package_small.part*"
foreach ($part in $parts) {
    # Check if already exists and valid
    try {
        $remote_size_str = ssh -i $key -o StrictHostKeyChecking=no $remote "stat -c %s ${remote_path}/$($part.Name)" 2>$null
        if ($LASTEXITCODE -eq 0 -and [int64]$remote_size_str -eq $part.Length) {
            Write-Host "Skipping $($part.Name) (already exists)"
            continue
        }
    } catch {}

    $retries = 5
    $success = $false
    while ($retries -gt 0 -and -not $success) {
        try {
            Write-Host "Uploading $($part.Name)..."
            scp -i $key -o StrictHostKeyChecking=no $part.FullName "${remote}:${remote_path}"
            
            # Verify size
            $remote_size_str = ssh -i $key -o StrictHostKeyChecking=no $remote "stat -c %s ${remote_path}/$($part.Name)"
            $remote_size = [int64]$remote_size_str
            if ($remote_size -eq $part.Length) {
                Write-Host "Success: $($part.Name)"
                $success = $true
            } else {
                Write-Host "Size mismatch: Local $($part.Length) vs Remote $remote_size"
                $retries--
            }
        } catch {
            Write-Host "Error uploading $($part.Name): $_"
            $retries--
            Start-Sleep -Seconds 2
        }
    }
    
    if (-not $success) {
        Write-Error "Failed to upload $($part.Name) after retries."
        exit 1
    }
}

Write-Host "All parts uploaded."
