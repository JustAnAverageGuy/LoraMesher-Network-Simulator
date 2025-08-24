const socket = io();
const svg = document.getElementById("svg");
const tooltip = document.getElementById("tooltip");
const nodesGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");

const simulationDurationInput = document.getElementById("sim-duration");
const enableSimulationCheckBox = document.getElementById("enable-simulation");
const newNodeAdditionIntervalInput = document.getElementById("new-node-interval");

svg.appendChild(nodesGroup);

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
}

// TOOLTIP HANDLING{{{

function showTooltip(evt, node) {// {{{
  let html = `<strong>${node.name}</strong> (${node.role})<br>`;
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
    html += "<table><thead><tr><th>dst</th><th>via</th><th>metric</th><th>role</th></tr></thead><tbody>";
    node.routes.forEach(r => {
      html += `<tr><td>${r.dst}</td><td>${r.via}</td><td>${r.metric}</td><td>${r.role}</td></tr>`;
    });
    html += "</tbody></table>";
  } else {
    html += "<em>No routes</em>";
  }
  tooltip.innerHTML = html;
  tooltip.style.display = "block";
  positionTooltip(evt);
} // }}}

function positionTooltip(evt) {// {{{
  const tooltipRect = tooltip.getBoundingClientRect();
  const svgRect = svg.getBoundingClientRect();

  let left = evt.clientX - svgRect.left + 10;
  let top = evt.clientY - svgRect.top + 10;

  // Prevent right overflow
  if (left + tooltipRect.width > svg.clientWidth) {
    left = evt.clientX - svgRect.left - tooltipRect.width - 10;
  }
  // Prevent bottom overflow
  if (top + tooltipRect.height > svg.clientHeight) {
    top = evt.clientY - svgRect.top - tooltipRect.height - 10;
  }

  tooltip.style.left = left + "px";
  tooltip.style.top = top + "px";
} // }}}

function moveTooltip(evt) {// {{{
  positionTooltip(evt);
} // }}}

function hideTooltip() {// {{{
  tooltip.style.display = "none";
} // }}}

//}}}

// GRAPH RENDERING {{{

function clearSvg() {
  while (nodesGroup.firstChild) nodesGroup.removeChild(nodesGroup.firstChild);
}

function render(nodes) {
  clearSvg();
  const width = svg.clientWidth;
  const height = svg.clientHeight;

  const nodeElementsMap = {}; // store circle + range for quick lookup

  const screenPos = nodes.map(n => ({
    name: n.name,
    x: (n.x / SIZE_KM) * width,
    y: (n.y / SIZE_KM) * height,
  }));

  const rScreen = (CONNECTION_RANGE_KM / SIZE_KM) * Math.min(width, height);

  console.table({
    width,
    height,
    SIZE_KM,
    CONNECTION_RANGE_KM,
    rScreen,
  });

  // Connections
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist2 = dx * dx + dy * dy;
      if (dist2 <= CONNECTION_RANGE_KM * CONNECTION_RANGE_KM) {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", screenPos[i].x);
        line.setAttribute("y1", screenPos[i].y);
        line.setAttribute("x2", screenPos[j].x);
        line.setAttribute("y2", screenPos[j].y);
        line.setAttribute("stroke", "green");
        line.setAttribute("stroke-width", "1");
        line.setAttribute("opacity", "0.5");
        nodesGroup.appendChild(line);
      }
    }
  }

  // Nodes
  nodes.forEach(n => {
    const cx = (n.x / SIZE_KM) * width;
    const cy = (n.y / SIZE_KM) * height;

    const r = (CONNECTION_RANGE_KM / SIZE_KM) * Math.min(width, height);
    const circ = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circ.setAttribute("cx", cx);
    circ.setAttribute("cy", cy);
    circ.setAttribute("r", r);
    circ.setAttribute("fill", "none");
    circ.setAttribute("stroke", "#bbb");
    circ.setAttribute("stroke-width", "1");
    circ.setAttribute("opacity", "0.7");
    nodesGroup.appendChild(circ);

    const nodeC = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    nodeC.setAttribute("cx", cx);
    nodeC.setAttribute("cy", cy);
    nodeC.setAttribute("r", 6);
    const isGateway = n.role == "GATEWAY";
    const isSensor = n.role == "SENSOR";
    nodeC.setAttribute("fill", isGateway ? "red" : isSensor ? "purple" : "#007bff");
    nodeC.classList.add("node");
    nodeC.dataset.name = n.name;

    nodeC.addEventListener("mouseenter", e => {
      circ.classList.add("highlight-range");
      nodeC.classList.add("highlight-node");
      showTooltip(e, n);
    });
    nodeC.addEventListener("mousemove", moveTooltip);
    nodeC.addEventListener("mouseleave", () => {
      circ.classList.remove("highlight-range");
      nodeC.classList.remove("highlight-node");
      hideTooltip();
    });

    nodesGroup.appendChild(nodeC);

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", cx + 8);
    label.setAttribute("y", cy + 4);
    label.setAttribute("font-size", "12");
    label.textContent = n.name;
    nodesGroup.appendChild(label);

    // store for sidepanel hover
    nodeElementsMap[n.name] = { nodeCircle: nodeC, rangeCircle: circ };
  });

  renderSidePanel(nodes, nodeElementsMap);
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
    thead.innerHTML = "<tr><th>dst</th><th>via</th><th>metric</th><th>rssi</th><th>snr</th><th>role</th></tr>";
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    n.routes.forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${r.dst}</td><td>${r.via}</td><td>${r.metric}</td><td>${r.rssi.toFixed(2)}</td><td>${r.snr.toFixed(2)}</td><td>${r.role}</td>`;
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
  socket.emit("set_reroute", { reroute_on_new_node: reroute });
  event.target.nextElementSibling.textContent = reroute ? "Yes" : "No";
});

// }}}

// SVG listener {{{
// Click to add node
svg.addEventListener("click", evt => {
  if (evt.target.classList.contains("node")) return;
  const rect = svg.getBoundingClientRect();
  const clickX = evt.offsetX;
  const clickY = evt.offsetY;
  const width = svg.clientWidth;
  const height = svg.clientHeight;
  const simX = (clickX / width) * SIZE_KM;
  const simY = (clickY / height) * SIZE_KM;
  const confirmAdd = confirm(`Create a new node at (${simX.toFixed(2)}, ${simY.toFixed(2)})?`);
  if (confirmAdd) {
    socket.emit("add_node", { position: [simX, simY] });
  }
});// }}}

// SOCKET listeners {{{
socket.on("connect", () => console.log(`${Date.now()} connected to server`));
socket.on("disconnect", () => console.log(`${Date.now()} disconnected from the server`));
socket.on("snapshot", data => {
  console.log(`SNAPSHOT RECEIVED`, data);
  render(data.nodes);
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
  <li class="list-group-item"><strong>Average Time to Deliver (s):</strong> ${data.average_time_to_deliver}</li>
  <li class="list-group-item"><strong>Total Routes Broadcasted:</strong> ${data.total_routes_broadcasted}</li>
  <li class="list-group-item"><strong>Average New Node Discovery Time (s):</strong> ${data.average_new_node_discovery_time}</li>
  <li class="list-group-item"><strong>New Nodes Added:</strong> ${data.new_nodes_added}</li>
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

// }}}

// vim: se fdm=marker:

