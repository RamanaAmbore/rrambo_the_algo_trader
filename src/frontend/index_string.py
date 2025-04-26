index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>rambo-the-algo</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #ffffff; /* Pure white */
                color: #333333; /* Soft dark gray for text */
            }

            .navbar {
                background-color: #f6f7f7; /* Navbar background stays */
                padding: 10px 20px;
                color: #333333;
                display: flex;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                border-bottom: 1px solid #f0f1f1; /* Changed to #f0f1f1 */
            }

            .navbar img {
                height: 45px;
                margin-right: 12px;
            }

            .navbar span {
                font-size: 1.3em;
                font-weight: bold;
            }

            .tab-headings {
                background-color: #f2f2f2; /* Tab background */
                padding: 6px 12px; /* Smaller vertical space */
                border-bottom: 1px solid #f0f1f1; /* Changed to #f0f1f1 */
                font-weight: 600;
                color: #333333;
            }

            .dash-tabs-container {
                border-bottom: 1px solid #f0f1f1; /* Changed to #f0f1f1 */
            }

            .dash-tabs-container button {
                padding: 6px 12px;
                margin: 0;
                background-color: #f7f7f7; /* Light gray for unselected tabs */
                border: none;
                border-right: 1px solid #f0f1f1; /* Changed to #f0f1f1 */
                font-weight: 500;
                color: #333;
            }
            
            .dash-tabs-container button.tab--selected {
                background-color: #d0d0d0; /* Proper gray for selected tab */
                font-weight: bold;
                border-top: 3px solid #f0f1f1; /* Changed to #f0f1f1 */
            }

            th {
                background-color: #f6f7f7 !important; /* Table heading background */
                color: #333333 !important;
                font-weight: 600;
                padding: 8px 10px;
                border: 1px solid #f0f1f1 !important; /* Changed to #f0f1f1 */
            }

            td {
                border: 1px solid #f0f1f1 !important; /* Changed to #f0f1f1 */
                padding: 6px 10px;
            }

            table {
                border: 1px solid #f0f1f1 !important; /* Changed to #f0f1f1 */
                border-collapse: collapse;
            }

            #loader-wrapper {
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #ffffff;
                z-index: 9999;
                flex-direction: column;
            }

            #loader-wrapper img {
                width: 100vw;
                height: 100vh;
                object-fit: fill;
                position: absolute;
                top: 0;
                left: 0;
                z-index: -1;
            }

            #loader-text {
                color: #333333;
                font-size: 2em;
                font-weight: bold;
                text-shadow: 1px 1px 4px rgba(255, 255, 255, 0.8);
                z-index: 10000;
            }

            button:focus {
                outline-color: #f0f1f1 !important; /* Changed to #f0f1f1 */
            }

footer {
                position: fixed;
                bottom: 0;
                width: 100%;
                background-color: #f0f1f1; /* Changed footer background to match border */
                padding: 6px 16px; /* Smaller vertical space */
                text-align: center;
                font-size: 0.8em;
                color: #555;
                box-shadow: 0 -1px 4px rgba(0,0,0,0.1);
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 6px;
                z-index: 1000;
            }

            footer img {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                object-fit: cover;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div id="loader-wrapper">
            <img src="/assets/loading.gif" alt="Loading...">
            <div id="loader-text">Loading...</div>
        </div>

        <div id="react-entry-point">
            {%app_entry%}
        </div>

        <footer>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>© 2025 Ramana Ambore, FRM, CFA Level 3 Candidate</span>
                <img src="/assets/ramana.jpg" alt="Ramana Ambore" />
            </div>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>

        <script>
            window.addEventListener('load', function () {
                setTimeout(function () {
                    const loader = document.getElementById('loader-wrapper');
                    if (loader) loader.style.display = 'none';
                }, 2000); // 2 seconds delay
            });
        </script>
    </body>
</html>

'''

