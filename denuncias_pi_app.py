from flask import Flask, request, redirect, url_for, render_template_string, jsonify
import os, json
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'  # Mude para uma chave segura
REPORTS_FILE = 'reports.json'  # Mudando para JSON para melhor estrutura
PIRACAIA_LAT = -23.05389
PIRACAIA_LNG = -46.35806

# Configurações para produção
class Config:
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

app.config.from_object(DevelopmentConfig)

# HTML templates melhorados
INDEX_HTML = '''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Denúncia de Crimes Ambientais - Piracaia</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    :root {
      --primary-color: #1b5e20;
      --secondary-color: #388e3c;
      --accent-color: #4caf50;
      --background-gradient: linear-gradient(135deg, #e0f7fa 0%, #f1f8e9 100%);
    }
    
    body{
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin:0;
      background: var(--background-gradient);
      min-height:100vh;
      display:flex;
      flex-direction:column;
      align-items:center;
      animation: fadeIn 1.5s ease-in-out;
    }
    
    @keyframes fadeIn {
      from {opacity:0; transform: translateY(20px);}
      to {opacity:1; transform: translateY(0);}
    }
    
    .header {
      background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
      color: white;
      width: 100%;
      padding: 1rem 0;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    h2{
      margin: 20px 0;
      color: var(--primary-color);
      text-align: center;
      animation: pulse 2s infinite;
    }
    
    .container {
      width: 90%;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    
    #map{
      height:450px;
      width:100%;
      border-radius:15px;
      margin-bottom:25px;
      box-shadow:0 8px 25px rgba(0,0,0,0.15);
      animation: zoomIn 1s;
      border: 3px solid white;
    }
    
    .form-container{
      background:white;
      padding:30px;
      border-radius:15px;
      box-shadow:0 8px 25px rgba(0,0,0,0.15);
      width:100%;
      max-width:700px;
      animation: slideInUp 1.5s;
      margin-bottom: 30px;
    }
    
    label{
      display:block;
      margin-top:15px;
      font-weight:600;
      color: var(--primary-color);
    }
    
    input,select,textarea{
      width:100%;
      padding:12px;
      border-radius:10px;
      border:2px solid #e0e0e0;
      transition: all .3s;
      font-size:16px;
      box-sizing: border-box;
    }
    
    input:focus,select:focus,textarea:focus{
      border-color: var(--accent-color);
      box-shadow:0 0 8px rgba(76,175,80,0.3);
      outline: none;
    }
    
    .btn{
      margin-top:15px;
      padding:12px 25px;
      border:none;
      border-radius:10px;
      background:linear-gradient(90deg, var(--secondary-color), var(--primary-color));
      color:white;
      cursor:pointer;
      font-weight:bold;
      transition:transform 0.3s, box-shadow 0.3s;
      font-size:16px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    
    .btn:hover{
      transform:translateY(-3px);
      box-shadow:0 5px 15px rgba(0,0,0,0.3);
    }
    
    .btn-secondary{
      background:linear-gradient(90deg,#455a64,#263238);
    }
    
    .btn-success {
      background:linear-gradient(90deg,#388e3c,#2e7d32);
    }
    
    .button-group {
      display: flex;
      gap: 15px;
      flex-wrap: wrap;
    }
    
    .stats {
      display: flex;
      justify-content: space-around;
      margin: 20px 0;
      flex-wrap: wrap;
      gap: 15px;
    }
    
    .stat-card {
      background: white;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      text-align: center;
      flex: 1;
      min-width: 150px;
    }
    
    .stat-number {
      font-size: 2rem;
      font-weight: bold;
      color: var(--primary-color);
    }
    
    .footer {
      margin-top: auto;
      padding: 20px;
      text-align: center;
      color: #666;
      width: 100%;
    }
    
    .loading {
      display: none;
      text-align: center;
      padding: 20px;
    }
    
    .spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid var(--primary-color);
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 2s linear infinite;
      margin: 0 auto;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .alert {
      padding: 15px;
      border-radius: 10px;
      margin: 15px 0;
      display: none;
    }
    
    .alert-success {
      background: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    }
    
    .alert-error {
      background: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    }
    
    @media (max-width: 768px) {
      .form-container {
        padding: 20px;
      }
      
      .button-group {
        flex-direction: column;
      }
      
      .btn {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1><i class="fas fa-tree"></i> Denúncias Ambientais - Piracaia</h1>
    <p>Proteja nosso meio ambiente - Registre denúncias de crimes ambientais</p>
  </div>

  <div class="container">
    <div class="stats" id="statsContainer">
      <!-- Estatísticas serão carregadas via JavaScript -->
    </div>

    <div id="alert" class="alert"></div>

    <div id="map"></div>

    <div class="form-container">
      <h2><i class="fas fa-map-marker-alt"></i> Registrar Nova Denúncia</h2>
      <p>Clique no mapa para selecionar a localização exata</p>
      
      <form id="reportForm" method="post" action="/submit">
        <input type="hidden" name="lat" id="lat" required>
        <input type="hidden" name="lng" id="lng" required>

        <label><i class="fas fa-user"></i> Nome Completo:</label>
        <input type="text" name="nome" required placeholder="Digite seu nome completo">

        <label><i class="fas fa-id-card"></i> CPF:</label>
        <input type="text" name="cpf" required placeholder="000.000.000-00" pattern="[0-9]{3}.[0-9]{3}.[0-9]{3}-[0-9]{2}">

        <label><i class="fas fa-exclamation-triangle"></i> Tipo de Crime Ambiental:</label>
        <select name="tipo" required>
          <option value="">Selecione o tipo de crime</option>
          <option value="desmatamento">Desmatamento Irregular</option>
          <option value="poluicao">Poluição de Rios/Lagos</option>
          <option value="caca">Caça/Tráfico de Fauna</option>
          <option value="queimada">Queimada Irregular</option>
          <option value="residuos">Descarte Irregular de Resíduos</option>
          <option value="outro">Outro Crime Ambiental</option>
        </select>

        <label><i class="fas fa-file-alt"></i> Descrição Detalhada:</label>
        <textarea name="descricao" rows="5" required placeholder="Descreva com detalhes o que está ocorrendo..."></textarea>

        <div class="button-group">
          <button type="submit" class="btn" id="submitBtn">
            <i class="fas fa-paper-plane"></i> Enviar Denúncia
          </button>
          <a href="/view" class="btn btn-success">
            <i class="fas fa-list"></i> Ver Denúncias
          </a>
          <button type="button" class="btn btn-secondary" onclick="showAbout()">
            <i class="fas fa-info-circle"></i> Quem Somos
          </button>
        </div>
      </form>
    </div>

    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>Processando sua denúncia...</p>
    </div>
  </div>

  <!-- Modal Quem Somos -->
  <div id="aboutModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; 
       background:rgba(0,0,0,0.8); justify-content:center; align-items:center; z-index:1000;">
    <div style="background:white; padding:30px; border-radius:15px; max-width:600px; width:90%; text-align:left; position:relative;">
      <h3><i class="fas fa-users"></i> Quem Somos</h3>
      <p>Somos um grupo de desenvolvimento da faculdade UNIVESP, comprometido com a proteção ambiental e o desenvolvimento de soluções tecnológicas para problemas reais da sociedade.</p>
      <p><strong>Projeto Integrador:</strong> Sistema de Denúncias Ambientais - Piracaia/SP</p>
      <p><strong>Desenvolvimento:</strong> Diogo Lindemuth Cerezer de Camargo</p>
      <p><strong>Objetivo:</strong> Facilitar o registro e acompanhamento de denúncias de crimes ambientais na região de Piracaia.</p>
      <button onclick="hideAbout()" style="position:absolute; top:15px; right:15px; border:none; background:var(--primary-color); color:white; padding:8px 12px; border-radius:50%; cursor:pointer; font-weight:bold;">X</button>
    </div>
  </div>

  <div class="footer">
    <p>&copy; 2024 UNIVESP - Projeto Integrador. Todos os direitos reservados.</p>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    // Inicialização do mapa
    const map = L.map('map').setView([{{ lat }}, {{ lng }}], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    let marker;
    map.on('click', function(e){
      const {lat, lng} = e.latlng;
      if(marker) {
        marker.setLatLng(e.latlng);
      } else {
        marker = L.marker(e.latlng, {
          draggable: true,
          icon: L.icon({
            iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
            shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41]
          })
        }).addTo(map);
        
        marker.on('dragend', function() {
          const position = marker.getLatLng();
          document.getElementById('lat').value = position.lat;
          document.getElementById('lng').value = position.lng;
        });
      }
      document.getElementById('lat').value = lat;
      document.getElementById('lng').value = lng;
    });
    
    // Valores padrão
    document.getElementById('lat').value = {{ lat }};
    document.getElementById('lng').value = {{ lng }};
    
    // Form submission
    document.getElementById('reportForm').addEventListener('submit', function(e) {
      const submitBtn = document.getElementById('submitBtn');
      const loading = document.getElementById('loading');
      
      submitBtn.disabled = true;
      loading.style.display = 'block';
    });
    
    // Carregar estatísticas
    async function loadStats() {
      try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('statsContainer').innerHTML = `
          <div class="stat-card">
            <div class="stat-number">${stats.total_reports}</div>
            <div>Total de Denúncias</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">${stats.this_month}</div>
            <div>Este Mês</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">${stats.types_count}</div>
            <div>Tipos de Crimes</div>
          </div>
        `;
      } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
      }
    }
    
    // Modal functions
    function showAbout() {
      document.getElementById('aboutModal').style.display = 'flex';
    }
    
    function hideAbout() {
      document.getElementById('aboutModal').style.display = 'none';
    }
    
    // Mostrar alerta se houver na URL
    function checkUrlAlert() {
      const urlParams = new URLSearchParams(window.location.search);
      const success = urlParams.get('success');
      const error = urlParams.get('error');
      
      const alertDiv = document.getElementById('alert');
      
      if (success) {
        alertDiv.className = 'alert alert-success';
        alertDiv.innerHTML = '<i class="fas fa-check-circle"></i> ' + decodeURIComponent(success);
        alertDiv.style.display = 'block';
      } else if (error) {
        alertDiv.className = 'alert alert-error';
        alertDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + decodeURIComponent(error);
        alertDiv.style.display = 'block';
      }
    }
    
    // Inicialização
    document.addEventListener('DOMContentLoaded', function() {
      loadStats();
      checkUrlAlert();
      
      // Adicionar máscara de CPF
      const cpfInput = document.querySelector('input[name="cpf"]');
      cpfInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\\D/g, '');
        if (value.length <= 11) {
          value = value.replace(/(\\d{3})(\\d)/, '$1.$2');
          value = value.replace(/(\\d{3})(\\d)/, '$1.$2');
          value = value.replace(/(\\d{3})(\\d{1,2})$/, '$1-$2');
          e.target.value = value;
        }
      });
    });
  </script>
</body>
</html>
'''

VIEW_HTML = '''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Denúncias Registradas - Piracaia</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #f1f8e9 0%, #e0f7fa 100%);
      text-align: center;
      padding: 0;
      margin: 0;
      animation: fadeIn 1.5s ease-in-out;
    }
    
    .header {
      background: linear-gradient(90deg, #1b5e20, #388e3c);
      color: white;
      padding: 1.5rem 0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    
    #map {
      height: 500px;
      width: 100%;
      border-radius: 15px;
      margin: 20px auto;
      box-shadow: 0 8px 25px rgba(0,0,0,0.15);
      animation: zoomIn 1s;
      border: 3px solid white;
    }
    
    .reports-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;
      margin: 30px 0;
    }
    
    .report-card {
      background: white;
      border-radius: 15px;
      padding: 20px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      text-align: left;
      transition: transform 0.3s, box-shadow 0.3s;
      border-left: 5px solid #388e3c;
    }
    
    .report-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .report-type {
      font-weight: bold;
      color: #1b5e20;
      margin-bottom: 10px;
      font-size: 1.1em;
    }
    
    .report-desc {
      color: #555;
      margin-bottom: 15px;
      line-height: 1.5;
    }
    
    .report-meta {
      font-size: 0.9em;
      color: #777;
      border-top: 1px solid #eee;
      padding-top: 10px;
    }
    
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin: 10px;
      padding: 12px 25px;
      text-decoration: none;
      background: linear-gradient(90deg, #388e3c, #1b5e20);
      color: white;
      border-radius: 10px;
      transition: transform 0.3s, box-shadow 0.3s;
      font-weight: bold;
    }
    
    .btn:hover {
      transform: translateY(-3px);
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .btn-secondary {
      background: linear-gradient(90deg, #455a64, #263238);
    }
    
    .filters {
      margin: 20px 0;
      display: flex;
      gap: 15px;
      justify-content: center;
      flex-wrap: wrap;
    }
    
    .filter-btn {
      padding: 10px 20px;
      border: 2px solid #388e3c;
      background: white;
      color: #388e3c;
      border-radius: 25px;
      cursor: pointer;
      transition: all 0.3s;
    }
    
    .filter-btn.active, .filter-btn:hover {
      background: #388e3c;
      color: white;
    }
    
    .no-reports {
      grid-column: 1 / -1;
      text-align: center;
      padding: 40px;
      color: #666;
    }
    
    @media (max-width: 768px) {
      .reports-grid {
        grid-template-columns: 1fr;
      }
      
      .filters {
        flex-direction: column;
        align-items: center;
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1><i class="fas fa-list-alt"></i> Denúncias Registradas</h1>
    <p>Visualize todas as denúncias de crimes ambientais em Piracaia</p>
  </div>

  <div class="container">
    <div id="map"></div>
    
    <div class="filters">
      <button class="filter-btn active" onclick="filterReports('all')">Todas</button>
      <button class="filter-btn" onclick="filterReports('desmatamento')">Desmatamento</button>
      <button class="filter-btn" onclick="filterReports('poluicao')">Poluição</button>
      <button class="filter-btn" onclick="filterReports('caca')">Caça</button>
      <button class="filter-btn" onclick="filterReports('queimada')">Queimadas</button>
      <button class="filter-btn" onclick="filterReports('residuos')">Resíduos</button>
      <button class="filter-btn" onclick="filterReports('outro')">Outros</button>
    </div>

    <div class="reports-grid" id="reportsContainer">
      <!-- Reports serão carregados via JavaScript -->
    </div>

    <div>
      <a href="/" class="btn"><i class="fas fa-arrow-left"></i> Voltar</a>
      <button class="btn btn-secondary" onclick="showAbout()"><i class="fas fa-info-circle"></i> Quem Somos</button>
    </div>
  </div>

  <!-- Modal Quem Somos -->
  <div id="aboutModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; 
       background:rgba(0,0,0,0.8); justify-content:center; align-items:center; z-index:1000;">
    <div style="background:white; padding:30px; border-radius:15px; max-width:600px; width:90%; text-align:left; position:relative;">
      <h3><i class="fas fa-users"></i> Quem Somos</h3>
      <p>Somos um grupo de desenvolvimento da faculdade UNIVESP, comprometido com a proteção ambiental.</p>
      <p><strong>Desenvolvimento:</strong> Diogo Lindemuth Cerezer de Camargo</p>
      <button onclick="hideAbout()" style="position:absolute; top:15px; right:15px; border:none; background:#1b5e20; color:white; padding:8px 12px; border-radius:50%; cursor:pointer; font-weight:bold;">X</button>
    </div>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    let allReports = [];
    let currentFilter = 'all';
    
    // Carregar denúncias
    async function loadReports() {
      try {
        const response = await fetch('/api/reports');
        allReports = await response.json();
        displayReports(allReports);
        initMap(allReports);
      } catch (error) {
        console.error('Erro ao carregar denúncias:', error);
        document.getElementById('reportsContainer').innerHTML = `
          <div class="no-reports">
            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 20px;"></i>
            <h3>Erro ao carregar denúncias</h3>
            <p>Tente recarregar a página</p>
          </div>
        `;
      }
    }
    
    // Exibir denúncias
    function displayReports(reports) {
      const container = document.getElementById('reportsContainer');
      
      if (reports.length === 0) {
        container.innerHTML = `
          <div class="no-reports">
            <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 20px;"></i>
            <h3>Nenhuma denúncia encontrada</h3>
            <p>Seja o primeiro a registrar uma denúncia ambiental</p>
          </div>
        `;
        return;
      }
      
      container.innerHTML = reports.map(report => `
        <div class="report-card" data-type="${report.tipo}">
          <div class="report-type">
            <i class="fas fa-${getReportIcon(report.tipo)}"></i>
            ${getReportTypeName(report.tipo)}
          </div>
          <div class="report-desc">${report.descricao}</div>
          <div class="report-meta">
            <div><strong>Localização:</strong> ${report.lat ? '📌 Especificada' : '📍 Não especificada'}</div>
            <div><strong>Data:</strong> ${new Date(report.timestamp).toLocaleDateString('pt-BR')}</div>
          </div>
        </div>
      `).join('');
    }
    
    // Filtrar denúncias
    function filterReports(type) {
      currentFilter = type;
      
      // Atualizar botões
      document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');
      
      const filtered = type === 'all' 
        ? allReports 
        : allReports.filter(report => report.tipo === type);
      
      displayReports(filtered);
      updateMapMarkers(filtered);
    }
    
    // Inicializar mapa
    function initMap(reports) {
      const map = L.map('map').setView([{{ lat }}, {{ lng }}], 12);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);
      
      window.reportsMap = map;
      window.mapMarkers = [];
      
      updateMapMarkers(reports);
    }
    
    // Atualizar marcadores do mapa
    function updateMapMarkers(reports) {
      // Limpar marcadores anteriores
      window.mapMarkers.forEach(marker => window.reportsMap.removeLayer(marker));
      window.mapMarkers = [];
      
      // Adicionar novos marcadores
      reports.forEach(report => {
        if (report.lat && report.lng) {
          const marker = L.marker([report.lat, report.lng])
            .addTo(window.reportsMap)
            .bindPopup(`
              <b>${getReportTypeName(report.tipo)}</b><br>
              ${report.descricao}<br>
              <small>${new Date(report.timestamp).toLocaleDateString('pt-BR')}</small>
            `);
          
          window.mapMarkers.push(marker);
        }
      });
      
      // Ajustar vista do mapa se houver marcadores
      if (window.mapMarkers.length > 0) {
        const group = new L.featureGroup(window.mapMarkers);
        window.reportsMap.fitBounds(group.getBounds().pad(0.1));
      }
    }
    
    // Utilitários
    function getReportIcon(type) {
      const icons = {
        'desmatamento': 'tree',
        'poluicao': 'tint',
        'caca': 'paw',
        'queimada': 'fire',
        'residuos': 'trash',
        'outro': 'exclamation-triangle'
      };
      return icons[type] || 'exclamation-circle';
    }
    
    function getReportTypeName(type) {
      const names = {
        'desmatamento': 'Desmatamento Irregular',
        'poluicao': 'Poluição de Rios/Lagos',
        'caca': 'Caça/Tráfico de Fauna',
        'queimada': 'Queimada Irregular',
        'residuos': 'Descarte Irregular de Resíduos',
        'outro': 'Outro Crime Ambiental'
      };
      return names[type] || type;
    }
    
    // Modal functions
    function showAbout() {
      document.getElementById('aboutModal').style.display = 'flex';
    }
    
    function hideAbout() {
      document.getElementById('aboutModal').style.display = 'none';
    }
    
    // Inicialização
    document.addEventListener('DOMContentLoaded', loadReports);
  </script>
</body>
</html>
'''

# Funções auxiliares
def load_reports():
    """Carrega denúncias do arquivo JSON"""
    if not os.path.exists(REPORTS_FILE):
        return []
    
    try:
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            reports = json.load(f)
            return sorted(reports, key=lambda x: x['timestamp'], reverse=True)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Erro ao carregar denúncias: {e}")
        return []

def save_report(report):
    """Salva uma nova denúncia"""
    try:
        reports = load_reports()
        reports.append(report)
        
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar denúncia: {e}")
        return False

def get_stats():
    """Calcula estatísticas das denúncias"""
    reports = load_reports()
    current_month = datetime.now(timezone.utc).strftime('%Y-%m')
    
    stats = {
        'total_reports': len(reports),
        'this_month': len([r for r in reports if r['timestamp'].startswith(current_month)]),
        'types_count': len(set(r['tipo'] for r in reports))
    }
    
    return stats

# Rotas da API
@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())

@app.route('/api/reports')
def api_reports():
    return jsonify(load_reports())

# Rotas principais
@app.route('/')
def index():
    return render_template_string(INDEX_HTML, lat=PIRACAIA_LAT, lng=PIRACAIA_LNG)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Coleta e valida dados
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        tipo = request.form.get('tipo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        lat = request.form.get('lat', '').strip()
        lng = request.form.get('lng', '').strip()
        
        # Validação básica
        if not all([nome, cpf, tipo, descricao]):
            return redirect('/?error=' + 'Todos os campos são obrigatórios')
        
        # Processa coordenadas
        try:
            latf = float(lat) if lat else None
            lngf = float(lng) if lng else None
        except ValueError:
            latf = lngf = None
        
        # Cria entrada
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'nome': nome,
            'cpf': cpf,
            'tipo': tipo,
            'descricao': descricao.replace('\n', ' '),
            'lat': latf,
            'lng': lngf
        }
        
        # Salva denúncia
        if save_report(entry):
            return redirect('/?success=' + 'Denúncia registrada com sucesso!')
        else:
            return redirect('/?error=' + 'Erro ao salvar denúncia')
            
    except Exception as e:
        print(f"Erro no submit: {e}")
        return redirect('/?error=' + 'Erro interno do servidor')

@app.route('/view')
def view_reports():
    reports = load_reports()
    return render_template_string(
        VIEW_HTML, 
        reports=reports, 
        reports_json=json.dumps(reports, ensure_ascii=False), 
        lat=PIRACAIA_LAT, 
        lng=PIRACAIA_LNG
    )

# Health check para monitoramento
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})

# Inicialização
def init_app():
    """Inicializa a aplicação"""
    # Garante que o diretório de dados existe
    os.makedirs(os.path.dirname(REPORTS_FILE) if os.path.dirname(REPORTS_FILE) else '.', exist_ok=True)
    
    # Cria arquivo se não existir
    if not os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    init_app()
    
    print("=" * 60)
    print("Sistema de Denúncias Ambientais - Piracaia")
    print("Desenvolvido por: Diogo Lindemuth Cerezer de Camargo")
    print("UNIVESP - Projeto Integrador")
    print("=" * 60)
    print(f"Servidor rodando em: http://0.0.0.0:5000")
    print(f"Acesso local: http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)