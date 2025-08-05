html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Point Display</title>
    <style>
        canvas {
            border: 1px solid black;
        }
        .label {
            position: absolute;
            font-size: 12px;
            color: blue;
        }
    </style>
</head>
<body>
    <h1>Points on Canvas</h1>
    <canvas id="canvas" width="1000" height="1000"></canvas>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // Points data from Python
        const points = %s;
        const DISTANCE = %s;

        // Draw points and labels on the canvas
        points.forEach((point, index) => {
            // Draw point
            ctx.beginPath();
            ctx.arc(point[0], point[1], 5, 0, Math.PI * 2, true);
            ctx.fillStyle = 'red';
            ctx.fill();

            // Draw label
            ctx.fillStyle = 'blue';
            ctx.fillText(`(${point[0]}, ${point[1]})`, point[0] + 10, point[1]);

            // Connect points within DISTANCE
            points.forEach((otherPoint, otherIndex) => {
                if (index !== otherIndex) {
                    const distance = Math.sqrt(Math.pow(point[0] - otherPoint[0], 2) + Math.pow(point[1] - otherPoint[1], 2));
                    if (distance < DISTANCE) {
                        ctx.beginPath();
                        ctx.moveTo(point[0], point[1]);
                        ctx.lineTo(otherPoint[0], otherPoint[1]);
                        ctx.strokeStyle = 'green';
                        ctx.stroke();
                    }
                }
            });
        });
    </script>
</body>
</html>
"""
