const socket = io();
const tooltip = document.getElementById("tooltip");

const simulationDurationInput = document.getElementById("sim-duration");
const enableSimulationCheckBox = document.getElementById("enable-simulation");
const newNodeAdditionIntervalInput = document.getElementById("new-node-interval");


//Map Settings
const map =  L.map('map').locate({setView: true, maxZoom: 16});
const initialLatLng = [28.6139, 77.2090]; // Default coordinates if geolocation fails
function onLocationFound(e) {
    var radius = e.accuracy;
    L.marker(e.latlng).addTo(map)
        .bindPopup("You are within " + radius + " meters from this point").openPopup();
    L.circle(e.latlng, radius).addTo(map);
    initialLatLng[0] = e.latlng.lat;
    initialLatLng[1] = e.latlng.lng;
    socket.emit("set_center", { position: [initialLatLng[0], initialLatLng[1]] });
}
function onLocationError(e) {
    console.warn(e.message);
    map.setView(initialLatLng, 13); // Set view to default coordinates
}
map.on('locationfound', onLocationFound);
map.on('locationerror', onLocationError);


// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);



// Controls
const slider = document.getElementById("num-nodes");
const nodeCountLabel = document.getElementById("num-nodes-label");

let SIZE_KM = state.size_km;
let CONNECTION_RANGE_KM = state.connection_range_km;

enableSimulationCheckBox.checked = localStorage.getItem("enableSimulation") === "true";
simulationDurationInput.value = localStorage.getItem("simDuration") || 1800;
newNodeAdditionIntervalInput.value = localStorage.getItem("newNodeInterval") || 60;

// till simulation duration fire new node addition event at regular intervals
if (enableSimulationCheckBox.checked) {
  console.log("Simulation enabled");
  const simDuration = parseInt(simulationDurationInput.value, 10) * 1000;
  const newNodeInterval = parseInt(newNodeAdditionIntervalInput.value, 10) * 1000;
  const startTime = Date.now();
  const intervalId = setInterval(() => {
    if (Date.now() - startTime >= simDuration) {
      clearInterval(intervalId);
      return;
    }
    socket.emit("add_node", { position: [Math.random() * SIZE_KM, Math.random() * SIZE_KM] });
  }, newNodeInterval);

  // start a timer on screen to show remaining time
  const timerSpan = document.getElementById("timer");
  let remainingTime = simDuration / 1000;
  timerSpan.textContent = `Time Remaining: ${remainingTime}s`;
  const timerId = setInterval(() => {
    remainingTime -= 1;
    if (remainingTime <= 0) {
      clearInterval(timerId);
      timerSpan.textContent = "Simulation Ended";
      socket.disconnect(); // Disconnect from server when timer completes
    } else {
      timerSpan.textContent = `Time Remaining: ${remainingTime}s`;
    }
  }, 1000);
}

// TOOLTIP HANDLING{{{

function update_tooltip(node){
  if (nodes[node.name] && nodes[node.name].marker.isPopupOpen())
  {
      let html = `<strong>${node.name}</strong> (${node.role})`;
      html += `<button name="${node.name}" id="delete-btn" style="color:red; border:none; padding:2px 6px; cursor:pointer;" onclick="removeNode(this.name)" title="Remove Node"><i class="bi bi-trash"></i></button><br>`;
      html += `Position: (${node.x.toFixed(2)}, ${node.y.toFixed(2)})<br>`;
      if (node.stats) {
        html += `<div><strong>Stats:</strong></div>`;
        html += `<table style="width:100%; border-collapse:collapse; margin-bottom:6px;">`;
        html += `<tbody>`;
        for (const [key, value] of Object.entries(node.stats)) {
          html += `<tr><td style="padding:2px 4px; border:1px solid #ddd;">${key}</td><td style="padding:2px 4px; border:1px solid #ddd;">${value}</td></tr>`;
        }
        html += `</tbody></table>`;
      }
      if (node.routes.length > 0) {
        html += '<table style="width:100%; border-collapse:collapse; margin-bottom:6px;"><thead><tr><th>dst</th><th>via</th><th>metric</th><th>role</th></tr></thead><tbody>';
        node.routes.forEach(r => {
          html += `<tr><td>${r.dst}</td><td>${r.via}</td><td>${r.metric}</td><td>${r.role}</td></tr>`;
        });
        html += "</tbody></table>";
      } else {
        html += "<em>No routes</em>";
      }
      nodes[node.name].marker.setPopupContent(html);
  }
}

function removeNode(name){
  if (nodes[name])
  {
    confirmation = confirm(`Are you sure you want to remove node ${name}?`);
    if (!confirmation) return;
    map.removeLayer(nodes[name].marker);
    map.removeLayer(nodes[name].circle);
    delete nodes[name];
    socket.emit("remove_node", { name });
    window.location.reload();
  }
}

// GRAPH RENDERING {{{
  
const nodes = {};
function clearMap(){
  Object.values(nodes).forEach(n=>{
    map.removeLayer(n.marker);
    map.removeLayer(n.circle);
  });
  for (const key in nodes) {
    delete nodes[key];
  }
}

function render_map(all_nodes){
  all_nodes.forEach(n=>{
    const name = n.name;
    const lat = n.x;
    const lon = n.y;
    const role = n.role;
    const color = role == "GATEWAY" ? 'blue' : (role == "SENSOR") ? 'purple' : 'gray';
    if (nodes[name])
    {
      nodes[name].marker.setLatLng([lat, lon]);
      nodes[name].circle.setLatLng([lat, lon]);
      update_tooltip(n);
    }
    else
    {
      // Create new Marker
      nodes[name] = {
        marker: L.circleMarker([lat, lon], {
        radius: 6,
        color: color,
        fillOpacity: 0.8
        }).bindPopup(`${name} (${role})`).addTo(map),
        circle: L.circle([lat, lon], {
            radius: CONNECTION_RANGE_KM * 1000, // e.g. connection range in meters
            color: "green",
            opacity: 0.3,
            fillOpacity: 0.05,
            interactive: false  
          }).addTo(map)
      }
      // highlight circle on marker hover
      nodes[name].marker.on('mouseover', function() {
        this.setStyle({ weight: 3 });
        nodes[name].circle.setStyle({ opacity: 0.5, fillOpacity: 0.1 });
      });
      nodes[name].marker.on('mouseout', function() {
        this.setStyle({ weight: 1 });
        nodes[name].circle.setStyle({ opacity: 0.3, fillOpacity: 0.05 });
      });
    }
  })
}


function renderSidePanel(nodes, nodeElementsMap) {
  const list = document.getElementById("nodes-list");
  list.innerHTML = "";
  nodes.forEach(n => {
    const div = document.createElement("div");
    div.className = "node-entry";
    div.innerHTML = `<strong>${n.name}</strong> (${n.role})<br/>`;

    // Scrollable table container
    const wrapper = document.createElement("div");
    wrapper.className = "routes-wrapper";

    const table = document.createElement("table");
    table.className = "routes-table table table-sm";
    const thead = document.createElement("thead");
    thead.innerHTML = "<tr><th>dst</th><th>via</th><th>metric</th><th>snr</th><th>role</th></tr>";
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    n.routes.forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${r.dst}</td><td>${r.via}</td><td>${r.metric}</td><td>${r.snr.toFixed(2)}</td><td>${r.role}</td>`;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    wrapper.appendChild(table);
    div.appendChild(wrapper);

    // Hover highlight in visualization
    div.addEventListener("mouseenter", () => {
      const { nodeCircle, rangeCircle } = nodeElementsMap[n.name];
      nodeCircle.classList.add("highlight-node");
      rangeCircle.classList.add("highlight-range");
    });
    div.addEventListener("mouseleave", () => {
      const { nodeCircle, rangeCircle } = nodeElementsMap[n.name];
      nodeCircle.classList.remove("highlight-node");
      rangeCircle.classList.remove("highlight-range");
    });

    list.appendChild(div);
  });
}

// }}}

// SETUP EVENT HANDLERS{{{

// SLIDERS and BUTTONS  {{{

slider.addEventListener("input", () => {
  nodeCountLabel.textContent = slider.value;
});

/* slider.addEventListener("change", () => {
  const numNodes = document.getElementById("num-nodes").value;
  const connectionRange = document.getElementById("connection-range").value;
  const areaLength = document.getElementById("area-length").value;
  CONNECTION_RANGE_KM = parseInt(connectionRange, 10);
  SIZE_KM = parseInt(areaLength, 10);

  const updatedValues = {
    num_nodes: parseInt(numNodes, 10),
    connection_range: parseInt(connectionRange, 10),
    area_length: parseInt(areaLength, 10),
  };
  socket.emit("update", updatedValues);
  console.log(`Update emitted with updatedValues = `, updatedValues);
}); */

document.getElementById("reset-button").addEventListener("click", event => {
  event.preventDefault();
  document.getElementById("num-nodes").value = state.n;
  document.getElementById("connection-range").value = state.connection_range_km;
  document.getElementById("area-length").value = state.size_km;
  SIZE_KM = state.size_km;
  CONNECTION_RANGE_KM = state.connection_range_km;
  document.getElementById("sf").value = state.sf;
  document.getElementById("tx-power").value = state.tx_power_dbm;
  document.getElementById("path-loss-exponent").value = state.path_loss_exponent;
  socket.emit("reset");
  window.location.reload();
});

document.getElementById("update-button").addEventListener("click", event => {
  event.preventDefault();
  const numNodes = document.getElementById("num-nodes").value;
  const areaLength = document.getElementById("area-length").value;
  SIZE_KM = parseInt(areaLength, 10);
  const sf = document.getElementById("sf").value;
  const txPower = document.getElementById("tx-power").value;
  const pathLossExponent = document.getElementById("path-loss-exponent").value;
  const routingInterval = document.getElementById("routing-interval").value;
  const dataInterval = document.getElementById("data-interval").value;
  const reroute = document.getElementById("reroute-switch").checked;
  socket.emit("update", {
    num_nodes: parseInt(numNodes, 10),
    area_length: parseInt(areaLength, 10),
    sf: parseInt(sf, 10),
    tx_power: parseInt(txPower, 10),
    path_loss_exp: parseFloat(pathLossExponent),
    routing_interval: parseInt(routingInterval, 10),
    data_interval: parseInt(dataInterval, 10),
    reroute_on_new_node: reroute,
  });
  window.location.reload();
});

document.getElementById("reroute-switch").addEventListener("change", event => {
  const reroute = event.target.checked;
  event.target.nextElementSibling.textContent = reroute ? "Yes" : "No";
});

// }}}

// SVG listener {{{
// Click to add node
// Listen for click events on the Leaflet map
map.on('click', function (e) {
  // e.latlng contains the geographic coordinates of the click
  const lat = e.latlng.lat;
  const lon = e.latlng.lng;

  const confirmAdd = confirm(`Create a new node at:\nLatitude: ${lat.toFixed(5)}\nLongitude: ${lon.toFixed(5)} ?`);

  if (confirmAdd) {
    // Send to backend via WebSocket (adjust your socket.emit or fetch call)
    socket.emit("add_node", { position: [lat, lon] });
  }
});


// SOCKET listeners {{{
socket.on("connect", () => console.log(`${Date.now()} connected to server`));
socket.on("disconnect", () => console.log(`${Date.now()} disconnected from the server`));
socket.on("snapshot", data => {
  console.log(`SNAPSHOT RECEIVED`, data);
  render_map(data.nodes);
});
socket.on("range_update", data => {
  console.log("Received range update:", data);
  CONNECTION_RANGE_KM = data.connection_range_km;
  document.getElementById("connection-range").value = CONNECTION_RANGE_KM;
  console.log("Connection range updated to:", CONNECTION_RANGE_KM);
});

socket.on("statistics", data => {
  console.log("Statistics update:", data);
  const stats = document.querySelector(".card-body ul");
  stats.innerHTML = `
  <li class="list-group-item"><strong>Total Messages Sent:</strong> ${data.total_messages_sent}</li>
  <li class="list-group-item"><strong>Total Messages Received:</strong> ${data.total_messages_received}</li>
  <li class="list-group-item"><strong>Average Time to Deliver (ms):</strong> ${data.average_time_to_deliver * 1000}</li>
  <li class="list-group-item"><strong>Total Routes Broadcasted:</strong> ${data.total_routes_broadcasted}</li>
  <li class="list-group-item"><strong>Average New Node Discovery Time (s):</strong> ${data.average_new_node_discovery_time}</li>
  <li class="list-group-item"><strong>New Nodes Added:</strong> ${data.new_nodes_added}</li>
  <li class="list-group-item"><strong>Initial Broadcast Messages Sent:</strong> ${data.initial_broadcast_messages_sent}</li>
`;
});
// }}}

enableSimulationCheckBox.addEventListener("change", event => {
  localStorage.setItem("enableSimulation", event.target.checked);
});

simulationDurationInput.addEventListener("change", event => {
  localStorage.setItem("simDuration", event.target.value);
});

newNodeAdditionIntervalInput.addEventListener("change", event => {
  localStorage.setItem("newNodeInterval", event.target.value);
});

const downloadBtn = document.getElementById("download-btn");
downloadBtn.addEventListener("click", () => {
  // create a txt file of the format node_name,x,y,role
  socket.emit("download_topology");
  socket.once("topology_data", data => {
    console.table(data['nodes']);
    const textData = "name,x,y,role\n" + data['nodes'].map(n => `${n.name},${n.x},${n.y},${n.role}`).join("\n");
    const blob = new Blob([textData], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "topology.tlg";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
});

const uploadBtn = document.getElementById("upload-btn");
uploadBtn.addEventListener("click", () => {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".tlg,.txt";
  input.click();
  input.addEventListener("change", () => {
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = e => {
      const content = e.target.result;
      // parse the content
      const lines = content.split("\n").filter(line => line.trim() !== "");
      const nodes = [];
      for (let i = 1; i < lines.length; i++) {
        const [name, x, y, role] = lines[i].split(",");
        if (name && x && y && role) {
          nodes.push({ name: name.trim(), x: parseFloat(x), y: parseFloat(y), role: role.trim() });
        }
      }
      console.log("Parsed nodes from file:", nodes);
      socket.emit("load_topology", { nodes });
      window.location.reload();
    };
    reader.readAsText(file);
  });
});



// }}}

// vim: se fdm=marker:

