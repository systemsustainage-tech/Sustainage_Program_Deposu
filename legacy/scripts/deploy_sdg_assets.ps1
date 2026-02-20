$server = "72.62.150.207"
$user = "root"
$remote_base = "/var/www/sustainage"

# Create directories if not exist
ssh $user@$server "mkdir -p $remote_base/static/images"

# Copy images (1.png to 17.png)
for ($i=1; $i -le 17; $i++) {
    $file = "c:\SUSTAINAGESERVER\static\images\$i.png"
    if (Test-Path $file) {
        scp $file $user@$server`:$remote_base/static/images/
    }
}

# Copy Excel file for mapping
scp "c:\SUSTAINAGESERVER\SDG_232.xlsx" $user@$server`:$remote_base/

# Ensure permissions
ssh $user@$server "chown -R www-data:www-data $remote_base/static/images $remote_base/SDG_232.xlsx"

echo "SDG Assets deployed successfully."
