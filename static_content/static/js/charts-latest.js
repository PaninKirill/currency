$(document).ready(function(){
    var options = {
        bezierCurve : false
    };
    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [{% for item in object_list %}'{{item.get_currency_display}}',{% endfor %}],
            datasets: [{
                label: 'Buy',
                data: [{% for item in object_list %}'{{item.source}}',{% endfor %}],

                backgroundColor: [
                    'rgba(190, 247, 45, 0.1)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1,
            },
            {
                label: 'Sale',
                data: [{% for item in object_list %}{% if item.sale != 0.0 %}'{{item.sale}}'{% endif %},{% endfor %}, [{% for item in object_list %}'{{item.buy}}',{% endfor %}]],

                backgroundColor: [
                    'rgba(116, 167, 247, 0.1)'
                ],
                borderColor: [
                    'rgba(0, 99, 132, 1)',
                    'rgba(0, 162, 235, 1)',
                    'rgba(0, 206, 86, 1)',
                    'rgba(0, 192, 192, 1)',
                    'rgba(0, 102, 255, 1)',
                    'rgba(0, 159, 64, 1)'
                ],
                borderWidth: 1,
            },]
        },
        options: {
        legend: {
            display: true,
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: false,
                    }
                }]
            }
        }
    });
});
