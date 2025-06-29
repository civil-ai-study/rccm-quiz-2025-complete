// 分野別正答率グラフ描画
window.addEventListener('DOMContentLoaded', function() {
    // HTML内のscriptタグからデータを取得
    const raw = document.getElementById('category-data').textContent;
    let dict = {};
    try {
        dict = JSON.parse(raw);
    } catch (e) {
        dict = {};
    }
    // 辞書から配列に変換
    const categoryData = Object.entries(dict).map(([name, detail]) => ({
        name: name,
        accuracy: detail && detail.accuracy ? parseFloat(detail.accuracy) : 0.0
    }));
    const ctx = document.getElementById('categoryBarChart').getContext('2d');
    const barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categoryData.map(d => d.name),
            datasets: [{
                label: '正答率（%）',
                data: categoryData.map(d => d.accuracy),
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: '正答率（%）' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}); 