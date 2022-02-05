param (

    # The root directory to perform the pull in
    $baseDir = "."
)

function Go () {

    # microservices folders to install in local mvn repo
    $folders = @('microservice_backend_asset',
    'microservice_device_entrypoint'
    'microservice_timer_evaluation' ,
    'microservice_mqtt_publisher',
    #'reverse_proxy'
    #'redis'
    )

    ForEach ($folder in $folders) {

        Write-Host "Performing docker buildx of : '$folder'..." -foregroundColor "green"

        # Go into the folder
        Push-Location $folder

        # Perform the command within the folder
        & docker buildx build --platform linux/amd64,linux/arm/v7 -t dimax94/$folder --push .

	# Go back to the original folder
        Pop-Location
    }
}

function Main () {
    Go
}

# Executes the main function
Main
