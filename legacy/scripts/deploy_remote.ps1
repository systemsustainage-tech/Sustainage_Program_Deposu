$ErrorActionPreference = "Stop"

Write-Host "Starting Deployment to 72.62.150.207..."

# 1. Package the application
Write-Host "Step 1: Packaging application files..."
if (Test-Path "deploy_package_v3.tar.gz") {
    Remove-Item "deploy_package_v3.tar.gz" -ErrorAction SilentlyContinue
}
try {
    tar --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' --exclude='venv' --exclude='deploy_package.tar.gz' --exclude='deploy_package_v2.tar.gz' --exclude='deploy_package_v3.tar.gz' --exclude='logs' --exclude='*.db' --exclude='*.sqlite' --exclude='*.part*' --exclude='*.psd' --exclude='*.pdf' -czf deploy_package_v3.tar.gz *
    Write-Host "Package created: deploy_package_v3.tar.gz"
} catch {
    Write-Error "Failed to create package. Ensure 'tar' is installed."
    exit 1
}

# 2. Upload Package
Write-Host "Step 2: Uploading package..."
scp -i C:\Users\admin2\.ssh\id_ed25519 -o StrictHostKeyChecking=no deploy_package_v3.tar.gz root@72.62.150.207:/var/www/sustainage/

# 3. Upload Setup Script
Write-Host "Step 3: Uploading setup script..."
scp -i C:\Users\admin2\.ssh\id_ed25519 -o StrictHostKeyChecking=no remote_setup_systemd.sh root@72.62.150.207:/var/www/sustainage/

# 4. Execute Remote Setup
Write-Host "Step 4: Executing remote setup..."
ssh -i C:\Users\admin2\.ssh\id_ed25519 -o StrictHostKeyChecking=no -t root@72.62.150.207 "chmod +x /var/www/sustainage/remote_setup_systemd.sh && /var/www/sustainage/remote_setup_systemd.sh"

Write-Host "Deployment Complete! Check http://72.62.150.207:5001"
