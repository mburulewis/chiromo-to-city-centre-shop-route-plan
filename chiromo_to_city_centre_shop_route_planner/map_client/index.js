;(function (geoJSONData) {
  const wrapper = document.querySelector('.wrapper');
  const navigateButton = document.querySelector('span#navigate');
  navigateButton.style.display = 'none';
  const hideSidebarClass = 'hide-sidebar';
  const map = L.map('map-container', {
    center: [-1.2787710799462924, 36.813039779663086],
    zoom: 15,
    maxBounds: [[-1.2943000, 36.7961000], [-1.2693000, 36.8397000]],
    layers: [],
    maxZoom: 18,
    minZoom: 15,
    worldCopyJump: false,
    crs: L.CRS.EPSG3857
  });
  const baseLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    "attribution": null,
    "detectRetina": false,
    "noWrap": false,
    "subdomains": "abc"
  }).addTo(map);
  let geoJSON = L.geoJson(geoJSONData, {
    pointToLayer(geoJsonPoint, latlng) {
      return L.marker(latlng).bindTooltip(geoJsonPoint.properties.title);
    }
  }).addTo(map);
  geoJSON.setStyle(function (feature) {
    return feature.properties.style;
  });

  if(window.location.href.startsWith('http')){
    navigateButton.style.display = 'block';
    wrapper.classList.remove(hideSidebarClass);
    navigateButton.addEventListener('click', (e) => {
      wrapper.classList.toggle(hideSidebarClass);
    });
    geoJSON.remove();
    const socket = io();
    socket.on('connect', () => {
      console.log('Connected to websocket');
    });
    const currentPoints = [];
    const markers = [];
    let container;
    const searchBoxFunc = (el, i, arr) => {
      const span = el.parentElement.querySelector('span');
      i !== arr.length - 1 && span && span.addEventListener('click', () => {
        currentPoints.splice(i, 1);
        span.parentElement.remove();
        [...document.querySelectorAll('.box1 input[type="text"]')].forEach(searchBoxFunc)
      });
      el.oninput = ({target}) => {
        const place = target.value;    
        socket.emit('find', {place}, ({points = []} = {}) => {
          const collapsibleEls = [];
          if(container){
            container.remove();
            markers[i] && markers[i].remove();
          }
          if(!points.length){
            container = document.createElement('p');
            container.innerText = "Place not found";
            container.style.color = 'red';
            container.style.textAlign = 'center';
            container.style.width = '100%';
            el.parentElement.appendChild(container);
            return;
          }
          container = document.createElement('ul');
          container.style.border = '1px solid black';
          container.style.textAlign = 'center';
          container.style.width = '96%';
          container.style.maxHeight = '200px';
          container.style.listStyleType = 'none';
          container.style.overflowY = 'scroll';
          points.forEach((p, index) => {
            const listItem = document.createElement('li');
            const {name} = p.tags;
            listItem.className = "collapsible-item";
            listItem.innerText = name;
            listItem.onclick = () => {
              el.value = name;
              container.remove();
              socket.emit('coords', {points, index}, ({node}) => {
                markers[i] = L.marker({
                  lat: node.lat, lon: node.lon
                }).bindTooltip(name).addTo(map);
                currentPoints.splice(i, 0, node);
              });
            };
            container.appendChild(listItem);
          });
          el.parentElement.appendChild(container);
        });
      };
    };
    document.querySelector('.box1 button#add').addEventListener('click', (el) => {
      const div = document.createElement('div');
      const input = document.createElement('input');
      const span = document.createElement('span');
      div.className = "form-group";
      input.type = 'text';
      input.placeholder = 'jamia';
      input.required = true;
      div.appendChild(span);
      div.appendChild(input);
      const lastFG = document.querySelector('.box1 .form-group:last-of-type');
      lastFG.parentElement.insertBefore(div, lastFG);
      
      [...document.querySelectorAll('.box1 input[type="text"]')].forEach(searchBoxFunc);
    });
    document.querySelector('.box1 button#submit').addEventListener('click', ({target}) => {
      socket.emit('route', {points: currentPoints}, (data) => {
        geoJSON.remove();
        geoJSON = L.geoJson(data, {
          pointToLayer(geoJsonPoint, latlng) {
            return L.marker(latlng).bindTooltip(geoJsonPoint.properties.title);
          }
        }).addTo(map);
        geoJSON.setStyle(function (feature) {
          return feature.properties.style;
        });
      });
    });
    [...document.querySelectorAll('.box1 input[type="text"]')].forEach(searchBoxFunc);
  }
})({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {}, 'geometry': {'type': 'LineString', 'coordinates': [[36.8067379, -1.2726152], [36.8066773, -1.2731641], [36.806926, -1.2731713], [36.806918, -1.2738187], [36.8071484, -1.2738131], [36.8071406, -1.274127], [36.8074946, -1.2741994], [36.807736, -1.2742397], [36.8078996, -1.2742531], [36.8080043, -1.2745105], [36.8080127, -1.2745388], [36.808268, -1.2745088], [36.8085512, -1.2745345], [36.8090748, -1.2746375], [36.8096756, -1.2747748], [36.8100533, -1.2749293], [36.8103108, -1.2751352], [36.8106198, -1.2754613], [36.8109147, -1.2758175], [36.8110747, -1.2760105], [36.8113836, -1.2764223], [36.8115467, -1.2766798], [36.8117012, -1.2769115], [36.8117356, -1.2770316], [36.8117012, -1.2771517], [36.8115982, -1.2772633], [36.8115553, -1.2773834], [36.8115982, -1.2775035], [36.812183, -1.2781681], [36.8124507, -1.2784882], [36.8124823, -1.2785247], [36.8128685, -1.2789709], [36.8130144, -1.2791597], [36.8131518, -1.2792455], [36.8133663, -1.2793227], [36.8136152, -1.2793313], [36.8137526, -1.2793828], [36.8138448, -1.2794705], [36.8138945, -1.2795825], [36.8139408, -1.2797354], [36.8143297, -1.2797006], [36.8143807, -1.2798427], [36.8144531, -1.2799017], [36.8145416, -1.2799258], [36.8146757, -1.2799526], [36.8147857, -1.279958], [36.8150081, -1.2798544], [36.8150733, -1.27974], [36.8153147, -1.279892], [36.8152767, -1.2799296], [36.8153458, -1.279955], [36.8154706, -1.2800815], [36.8155431, -1.2802375], [36.8158126, -1.2808421], [36.815859, -1.280943], [36.8159256, -1.2810337], [36.8160036, -1.2810975], [36.8152164, -1.2815961], [36.8152387, -1.2816814], [36.8152348, -1.2817348], [36.8153507, -1.2816794], [36.8154708, -1.2816107], [36.8157608, -1.2814708], [36.8164367, -1.2811144], [36.817145, -1.2807409], [36.817196, -1.280714], [36.8174115, -1.281211], [36.8175961, -1.2815853], [36.8181082, -1.2826176], [36.818253, -1.2829123], [36.8185916, -1.2827657], [36.8186325, -1.2828443], [36.8187843, -1.2831362], [36.8188687, -1.2830942], [36.8195326, -1.2827562], [36.819573, -1.2827368], [36.8197658, -1.2831039], [36.8198619, -1.2833314], [36.8202131, -1.2831797], [36.8203757, -1.2831094]]}}, {'type': 'Feature', 'properties': {'title': 'Start'}, 'geometry': {'type': 'Point', 'coordinates': [36.8067379, -1.2726152]}}, {'type': 'Feature', 'properties': {'title': 'End'}, 'geometry': {'type': 'Point', 'coordinates': [36.8203757, -1.2831094]}}]});
