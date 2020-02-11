Import-Module $env:sql_module_psm1

function GetImages {
    param(
        $image_arr
    )
    $image_vals = @()
    foreach ($image in $image_arr) {
        $image_length = $($image.Split(' ')).Length
        $image_name = $image.Split(' ')[$image_length - 1]
        try {
            $camera_uuid=$image_name.Split('_')[0]
        } catch {
            continue
        }
        $image_url=$('https://statictrafficcameras.s3.amazonaws.com/'+$image_name)
        $val_string = "('$camera_uuid', '$image_url')," 
        $image_vals += $val_string
    }
    return $image_vals
}

$base_url = 's3://statictrafficcameras/'
$camera_one_images = aws s3 ls $($base_url + 'OR00000001958')
$camera_two_images = aws s3 ls $($base_url + 'WA0000000419')

$all_image_vals = @()

$all_image_vals += GetImages -image_arr $camera_one_images
$all_image_vals += GetImages -image_arr $camera_two_images

# $string.Substring(0,$string.Length-1)

$base_insert = 'INSERT INTO Warehouse.dbo.StateTrafficCameras_MetaData (uuid, image_url) VALUES '
$insert_str = $base_insert

$counter = 0

foreach ($str in $all_image_vals) {
    if ($counter -lt 999) {
        $insert_str += $str
        $counter++
    } else {
        $insert_str = $insert_str.Substring(0,$insert_str.Length-1)
        try {
            QueryDB -query $insert_str -database "Warehouse"
        } catch {
            Write-Host $_.Exception.Message 
            Break
        }
        $insert_str = $base_insert
        $counter = 0
    }
}