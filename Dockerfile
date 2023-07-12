FROM python:3.12-rc-windowsservercore-ltsc2022
WORKDIR /app
# Requirements
COPY ./requirements.txt ./
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

COPY ./main.py ./start.ps1 ./
COPY ./images ./images
CMD powershell -Command \
    $process = Start-Process -FilePath "powershell" -ArgumentList "./start.ps1" -PassThru; \
    $result = $process.WaitForExit(5000); \
    if ($result) { \
    Write-Host "Exited with code $($process.ExitCode)"; \
    } else { \
    Stop-Process -Id $process.Id -Force; \
    Write-Host "Successful"; \
    }
