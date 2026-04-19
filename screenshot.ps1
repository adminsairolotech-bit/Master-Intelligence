Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$bounds = $screen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage $bitmap
$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bitmap.Save('C:\Users\Sai Rolotech\Desktop\AI-Command-Center-Preview.png')
$graphics.Dispose()
$bitmap.Dispose()
Write-Host 'Screenshot saved!'