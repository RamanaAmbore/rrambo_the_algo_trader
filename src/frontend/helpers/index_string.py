# Minimal index_string
index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rambo, the Algo</title>
        {%favicon%}
        {%css%}
    </head>
    <body>

        {%app_entry%}

        {%config%}
        {%scripts%}
        {%renderer%}

        <script>
            window.addEventListener('load', function () {
                setTimeout(function () {
                    const loader = document.getElementById('loader-wrapper');
                    if (loader) loader.style.display = 'none';
                }, 100);
            });
        </script>
    </body>
</html>
'''