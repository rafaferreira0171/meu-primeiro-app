const inputFile = document.querySelector('#excel-input');
const totalSalesEl = document.querySelector('#total-sales');
const avgTicketEl = document.querySelector('#avg-ticket');
const itemsPerServiceEl = document.querySelector('#items-per-service');
const rankingBody = document.querySelector('#ranking-body');
const chartCanvas = document.querySelector('#sales-chart');

let salesChart;

function toNumber(value) {
  if (typeof value === 'number') return value;
  if (!value) return 0;

  const normalized = String(value)
    .trim()
    .replace(/\s/g, '')
    .replace(/\./g, '')
    .replace(',', '.');

  return Number(normalized) || 0;
}

function formatCurrency(value) {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatDecimal(value) {
  return value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function renderRanking(rows) {
  rankingBody.innerHTML = '';

  if (!rows.length) {
    rankingBody.innerHTML = '<tr><td colspan="5" class="empty">Nenhum dado encontrado na planilha.</td></tr>';
    return;
  }

  rows.forEach((row, index) => {
    const tr = document.createElement('tr');
    if (index === 0) tr.classList.add('top-1');

    tr.innerHTML = `
      <td>${index + 1}</td>
      <td>${row.loja}</td>
      <td>${formatCurrency(row.vendas)}</td>
      <td>${formatDecimal(row.atendimentos)}</td>
      <td>${formatDecimal(row.pecas)}</td>
    `;

    rankingBody.appendChild(tr);
  });
}

function renderChart(rows) {
  const labels = rows.map((row) => row.loja);
  const salesData = rows.map((row) => row.vendas);

  if (salesChart) salesChart.destroy();

  salesChart = new Chart(chartCanvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Vendas (R$)',
          data: salesData,
          backgroundColor: '#2563eb',
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback(value) {
              return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
            },
          },
        },
      },
    },
  });
}

function processData(rawRows) {
  const mapped = rawRows
    .map((row) => ({
      loja: row.Loja || row.loja || '',
      vendas: toNumber(row.Vendas ?? row.vendas),
      atendimentos: toNumber(row.Atendimentos ?? row.atendimentos),
      pecas: toNumber(row['Peças'] ?? row.pecas ?? row.Pecas),
    }))
    .filter((row) => row.loja);

  const totalSales = mapped.reduce((sum, row) => sum + row.vendas, 0);
  const totalServices = mapped.reduce((sum, row) => sum + row.atendimentos, 0);
  const totalItems = mapped.reduce((sum, row) => sum + row.pecas, 0);

  const avgTicket = totalServices ? totalSales / totalServices : 0;
  const itemsPerService = totalServices ? totalItems / totalServices : 0;

  totalSalesEl.textContent = formatCurrency(totalSales);
  avgTicketEl.textContent = formatCurrency(avgTicket);
  itemsPerServiceEl.textContent = formatDecimal(itemsPerService);

  const ranking = [...mapped].sort((a, b) => b.vendas - a.vendas);
  renderRanking(ranking);
  renderChart(ranking);
}

inputFile.addEventListener('change', async (event) => {
  const [file] = event.target.files;
  if (!file) return;

  try {
    const buffer = await file.arrayBuffer();
    const workbook = XLSX.read(buffer, { type: 'array' });
    const firstSheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[firstSheetName];
    const rawRows = XLSX.utils.sheet_to_json(sheet, { defval: '' });

    processData(rawRows);
  } catch (error) {
    rankingBody.innerHTML = '<tr><td colspan="5" class="empty">Erro ao processar arquivo. Verifique o formato.</td></tr>';
    console.error(error);
  }
});
