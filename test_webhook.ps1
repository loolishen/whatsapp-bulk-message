$uri = "https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/"
$body = @{
    type = "message"
    data = @{
        from = "60162107682"
        message = "TEST"
        id = "test123"
        timestamp = "123"
    }
} | ConvertTo-Json

Write-Host "Testing webhook..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json"
    Write-Host "OK - Webhook responded: $response" -ForegroundColor Green
} catch {
    Write-Host "ERROR - Webhook error: $_" -ForegroundColor Red
}

