from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get(
    "/",
    summary="Root Page",
    description="Landing page with navigation buttons.",
    response_class=HTMLResponse
)
async def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Clashdog Home</title>
        <style>
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
                overflow: hidden;
                outline: none !important;
                border: none !important;
                background: transparent !important;
                box-shadow: none !important;
            }
            * {
                outline: none !important;
                border: none !important;
                box-shadow: none !important;
                /* REMOVE or comment out the next line: */
                /* background: transparent !important; */
            }
            *, *::before, *::after {
                box-sizing: border-box;
            }
            .bg-video {
                position: fixed;
                top: 0;
                left: 0;
                min-width: 100vw;
                min-height: 100vh;
                width: 100vw;
                height: 100vh;
                z-index: -1;
                object-fit: cover;
                filter: brightness(0.5) blur(0px);
            }
            .content {
                position: absolute;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .logo-group {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 2rem;
            }
            .logo-main {
                width: 220px;
                max-width: 80vw;
                margin-bottom: 1rem;
                opacity: 0.95;
            }
            .logo-claim {
                width: 320px;
                max-width: 90vw;
                opacity: 0.85;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 2rem;
                letter-spacing: 2px;
                color: #fff;
                text-shadow: 0 2px 8px #000;
            }
            .button-group {
                display: flex;
                gap: 2rem;
            }
            .nav-btn {
                min-width: 170px;
                padding: 1.1rem 2.7rem;
                font-size: 1.22rem;
                border: none;
                border-radius: 12px;
                background: #232526 !important; /* Solid grey background */
                color: #ff9800 !important;      /* Always orange text */
                cursor: pointer;
                transition: background 0.18s, color 0.18s, transform 0.18s, box-shadow 0.18s;
                box-shadow: 0 4px 18px rgba(255,152,0,0.18), 0 1.5px 8px rgba(0,0,0,0.13);
                font-weight: 700;
                letter-spacing: 1.2px;
                outline: none;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
                opacity: 1;
            }
            .nav-btn::before {
                content: "";
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(255,255,255,0.07);
                border-radius: 12px;
                opacity: 0;
                transition: opacity 0.18s;
                pointer-events: none;
            }
            .nav-btn:hover, .nav-btn:focus {
                background: linear-gradient(90deg, #ff9800 0%, #ff5722 100%);
                color: #fff !important; /* White text on hover */
                transform: translateY(-3px) scale(1.06);
                box-shadow: 0 6px 24px #ff9800a0, 0 2px 12px rgba(0,0,0,0.18);
                text-shadow: 0 2px 8px #23252688;
            }
            .nav-btn:hover::before, .nav-btn:focus::before {
                opacity: 1;
            }
        </style>
    </head>
    <body>
        <video class="bg-video" autoplay loop muted playsinline>
            <source src="https://cdn.streamonline.pro/clashofthestars-tv/18/18-clash-12-video-background.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <div class="content">
            <div class="logo-group">
                <img src="https://cdn.streamonline.pro/clashofthestars-tv/18/Logo-1.svg" alt="logo" class="logo-main">
                <img src="https://cdn.streamonline.pro/clashofthestars-tv/18/claim-1.png" alt="claim" class="logo-claim">
            </div>
            <h1>Welcome to Clashdog!</h1>
            <div class="button-group">
                <button class="nav-btn" onclick="location.href='/fighters'">Fighters</button>
                <button class="nav-btn" onclick="location.href='/tournaments'">Tournaments</button>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)