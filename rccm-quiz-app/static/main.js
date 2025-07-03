// 分野別正答率データ取得
let categoryData = [];
const catDataElem = document.getElementById('category-data');
if (catDataElem) {
    categoryData = JSON.parse(catDataElem.textContent);
}
// 成績推移データ取得（statistics.htmlのみ）
let dailyAccuracyList = [];
const dailyAccElem = document.getElementById('daily-accuracy-list');
if (dailyAccElem) {
    dailyAccuracyList = JSON.parse(dailyAccElem.textContent);
}
// 分野別正答率グラフ
if (categoryData.length && document.getElementById('categoryBarChart')) {
    const ctx = document.getElementById('categoryBarChart').getContext('2d');
    const barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categoryData.map(d => d.name),
            datasets: [{
                label: '正答率（%）',
                data: categoryData.map(d => d.accuracy),
                backgroundColor: categoryData.map(d => d.accuracy >= 80 ? '#4CAF50' : d.accuracy >= 50 ? '#FF9800' : '#F44336'),
                borderWidth: 1,
                barThickness: 18
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: false },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function(context) {
                            return context.parsed.x + '%';
                        }
                    }
                }
            },
            scales: {
                x: {
                    min: 0,
                    max: 100,
                    title: { display: true, text: '正答率（%）' },
                    ticks: { stepSize: 10, font: { size: 10 } }
                },
                y: {
                    title: { display: false },
                    ticks: { font: { size: 12 } }
                }
            },
            animation: {
                duration: 600,
                easing: 'easeOutQuart'
            }
        }
    });
}
// レーダーチャート（statistics.htmlのみ）
if (categoryData.length && document.getElementById('categoryRadarChart')) {
    const ctxRadar = document.getElementById('categoryRadarChart').getContext('2d');
    const radarChart = new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: categoryData.map(d => d.name),
            datasets: [{
                label: '分野別正答率',
                data: categoryData.map(d => d.accuracy),
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: false }
            },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: { stepSize: 20, font: { size: 10 } }
                }
            },
            animation: {
                duration: 600,
                easing: 'easeOutQuart'
            }
        }
    });
}
// 成績推移グラフ（日ごとの正答率%）（statistics.htmlのみ）
if (dailyAccuracyList.length && document.getElementById('accuracyTrendChart')) {
    const trendLabels = dailyAccuracyList.map(d => d.date);
    const trendData = dailyAccuracyList.map(d => d.accuracy);
    const ctxTrend = document.getElementById('accuracyTrendChart').getContext('2d');
    const trendChart = new Chart(ctxTrend, {
        type: 'bar',
        data: {
            labels: trendLabels,
            datasets: [{
                label: '正答率（%）',
                data: trendData,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: false }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    title: { display: true, text: '正答率（%）' },
                    ticks: { stepSize: 20 }
                }
            },
            animation: {
                duration: 600,
                easing: 'easeOutQuart'
            }
        }
    });
} 