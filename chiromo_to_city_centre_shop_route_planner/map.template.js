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
    let container;
    const searchBoxFunc = (el, i, arr) => {
      const span = el.parentElement.querySelector('span');
      i !== arr.length - 1 && span && span.addEventListener('click', () => {
        currentPoints.splice(i, 1);
        span.parentElement.remove();
        [...document.querySelectorAll('.box1 input[type="text"]')].forEach(searchBoxFunc)
      });
      el.onchange = ({target}) => {
        const place = target.value;    
        socket.emit('find', {place}, ({points = []} = {}) => {
          const collapsibleEls = [];
          if(container){
            container.remove();
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
            listItem.className = "collapsible-item";
            listItem.innerText = p.tags.name;
            listItem.onclick = () => {
              el.value = p.tags.name;
              container.remove();
              socket.emit('coords', {points, index}, (data) => {
                currentPoints[i] = data.node;
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
})(${geojson});
