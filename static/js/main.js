/**
 * Created by tdong on 22.08.16.
 */



$(document).ready(function() {


    $(".dropdown-menu li a").click(function(){

       // $(".btn:first-child").text($(this).text());
       // $(".btn:first-child").val($(this).text());

    });

    $('#input-chinese').on('keyup',function(e){
        if(e.keyCode === 13 ) {
            var ch_txt = $(this).val()
            console.log('received user input:',ch_txt)
            var ch_net = ask_for_ch_ldg_net(ch_txt)

        };
    });


})


function ask_for_ch_ldg_net(ch_txt) {
	$.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/make_net_from_chsnt",
        contentType:"text/json; charset=utf-8",
        data: {snt: ch_txt},
        beforeSend: function(){
            },
        success: function(data) {
            console.log(data);
            vis_dep(data, 'ch-canvas');
            test_vis_her('en-canvas')
            },
        error: function(jqXHR, textStatus, errorThrown) {
            alert(errorThrown);
            }
    });
}


function vis_dep(depJson, loc) {
    // create an array with nodes
    //OK!
    var vis_nodes0 = [];
	var vis_edges0 =[];

    for (var id in depJson) {
        var node0 = {},
            value = depJson[id];
        if (id === "-1"){
            node0['id'] = -1;
            node0['label'] = 'START';
            node0["color"] = '#ff00ff';
            vis_nodes0.push(node0);
            for (var rel in value['deps']){
                for (var toId in value['deps'][rel]){
                    var edge0 = {};
                    edge0['from'] = -1;
                    edge0['to'] = value['deps'][rel][toId];
                    edge0['arrows'] = 'to';
                    edge0["label"] = 'root';
                    edge0["color"] = '#ff00ff';
                    vis_edges0.push(edge0);
                }
            }
        }else{
            node0['id'] = id;
            node0['label'] = value['address']+":"+value['word']+":"+value['tag'];
            vis_nodes0.push(node0);
            for (var rel in value['deps']){
                for (var toId in value['deps'][rel]){
                    var edge0 = {};
                    edge0['from'] = id;
                    edge0['to'] = value['deps'][rel][toId];
                    edge0['arrows'] = 'to';
                    edge0["label"] = rel;
                    vis_edges0.push(edge0);
                }
            }
        }
    }

    var nodes = new vis.DataSet(vis_nodes0),
		// create an array with edges
        edges = new vis.DataSet(vis_edges0),
        // create a network
        container = document.getElementById(loc),
        data = {
				nodes: nodes,
				edges: edges
             	},
		options = {
            interaction:{
                        navigationButtons: true,
                        keyboard: true}

        },

		network = new vis.Network(container, data, options);
}


function test_arrow(){
    var nodes = null;
    var edges = null;
    var network = null;

    function destroy() {
      if (network !== null) {
        network.destroy();
        network = null;
      }
    }


      destroy();

      // create an array with nodes
      var nodes = [
        {id: 1, label: 'Node 1'},
        {id: 2, label: 'Node 2'},
        {id: 3, label: 'Node 3'},
        {id: 4, label: 'Node 4'},
        {id: 5, label: 'Node 5'}
      ];

      // create an array with edges
      var edges = new vis.DataSet([
        {from: 1, to: 3},
        {from: 1, to: 2},
        {from: 2, to: 4},
        {from: 2, to: 5}
      ]);

      // create a network
      var container = document.getElementById('ch-canvas');
      var data = {
        nodes: nodes,
        edges: edges
      };
      var options = {
        interaction: {
          navigationButtons: true,
          keyboard: true
        }
      };
      network = new vis.Network(container, data, options);

      // add event listeners
      network.on('select', function(params) {
        document.getElementById('selection').innerHTML = 'Selection: ' + params.nodes;
      });

}

function test_vis_her(where){
     // create an array with nodes
  var nodes = [
    {id: 1,  label: 'Node 1', color:'orange'},
    {id: 2,  label: 'Node 2', color:'DarkViolet', font:{color:'white'}},
    {id: 3,  label: 'Node 3', color:'orange'},
    {id: 4,  label: 'Node 4', color:'DarkViolet', font:{color:'white'}},
    {id: 5,  label: 'Node 5', color:'orange'},
    {id: 6,  label: 'cid = 1', cid:1, color:'orange'},
    {id: 7,  label: 'cid = 1', cid:1, color:'DarkViolet', font:{color:'white'}},
    {id: 8,  label: 'cid = 1', cid:1, color:'lime'},
    {id: 9,  label: 'cid = 1', cid:1, color:'orange'},
    {id: 10, label: 'cid = 1', cid:1, color:'lime'},
      {id: 11, label: 'cid = 2', cid:2, color:'lime'},
      {id: 12, label: 'cid = 2', cid:2, color:'lime'}
  ];

  // create an array with edges
  var edges = [
    {from: 1, to: 2},
    {from: 1, to: 3},
    {from: 10, to: 4},
    {from: 2, to: 5},
    {from: 6, to: 2},
    {from: 7, to: 5},
    {from: 8, to: 6},
    {from: 9, to: 7},
    {from: 10, to: 9},
    {from: 9, to: 11},
    {from: 11, to: 12}

  ];

    // create a network
    var container = document.getElementById(where);
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
                    layout:{randomSeed:8},
                    interaction:{
                        navigationButtons: true,
                        keyboard: true}};
    var network = new vis.Network(container, data, options);

    network.on("click", function(params) {
        console.log(params)
        if (params.nodes.length == 1) {
            if (network.isCluster(params.nodes[0]) == true) {
                network.openCluster(params.nodes[0]);
                }
            else {
                var cid = get_cid_of_node(nodes, params.nodes[0]);
                console.log(cid)
                if (cid !== -1) {
                    network.setData(data);
                    var clusterOptionsByData = {
                        joinCondition: function (childOptions) {
                            return childOptions.cid == cid;
                        },
                        clusterNodeProperties: {id: 'cidCluster', label: 'Cluster:'+cid.toString(), borderWidth: 3, shape: 'big circle'}
                    }
                    network.cluster(clusterOptionsByData);
                };
            }
        }

        });

    network.on("doubleClick", function(params) {
        network.setData(data);
        var cids = [1,2];
        var clusterOptionsByData;
        for (var i = 0; i < cids.length; i++) {
            var cid = cids[i];
            clusterOptionsByData = {
                joinCondition: function (childOptions) {
                    return childOptions.cid == cid; // the color is fully defined in the node.
                    },
                processProperties: function (clusterOptions, childNodes, childEdges) {
                  var totalMass = 0;
                  for (var i = 0; i < childNodes.length; i++) {
                      totalMass += childNodes[i].mass;
                  }
                  clusterOptions.mass = totalMass;
                  return clusterOptions;
                },
                clusterNodeProperties: {id: 'cluster:'+ cid, borderWidth: 3,
                    shape: 'big circle', label:'cluster:'+ cid}
            };
            network.cluster(clusterOptionsByData);
            }
        });

    function get_cid_of_node(nodes, nid){
        for (var index in nodes){
            var node = nodes[index];
            if (node['id'] === nid){
                return node['cid']
            }
        }
        return -1;

    }
}

function clusterByCid() {
      network.setData(data);
      var clusterOptionsByData = {
          joinCondition:function(childOptions) {
              return childOptions.cid == 1;
          },
          clusterNodeProperties: {id:'cidCluster', borderWidth:3, shape:'database'}
      };
      network.cluster(clusterOptionsByData);
  }

  function clusterByColor() {
      network.setData(data);
      var colors = ['orange','lime','DarkViolet'];
      var clusterOptionsByData;
      for (var i = 0; i < colors.length; i++) {
          var color = colors[i];
          clusterOptionsByData = {
              joinCondition: function (childOptions) {
                  return childOptions.color.background == color; // the color is fully defined in the node.
              },
              processProperties: function (clusterOptions, childNodes, childEdges) {
                  var totalMass = 0;
                  for (var i = 0; i < childNodes.length; i++) {
                      totalMass += childNodes[i].mass;
                  }
                  clusterOptions.mass = totalMass;
                  return clusterOptions;
              },
              clusterNodeProperties: {id: 'cluster:' + color, borderWidth: 3, shape: 'database', color:color, label:'color:' + color}
          };
          network.cluster(clusterOptionsByData);
      }
  }
  function clusterByConnection(network) {
      network.setData(data);
      network.clusterByConnection(1)
  }
  function clusterOutliers(network) {
      network.setData(data);
      network.clusterOutliers();
  }
  function clusterByHubsize(network) {
      network.setData(data);
      var clusterOptionsByData = {
          processProperties: function(clusterOptions, childNodes) {
            clusterOptions.label = "[" + childNodes.length + "]";
            return clusterOptions;
          },
          clusterNodeProperties: {borderWidth:3, shape:'box', font:{size:30}}
      };
      network.clusterByHubsize(undefined, clusterOptionsByData);
  }

function vis_dep_test(depJson, loc) {
    // create an array with nodes
    //OK!
    var nodes = new vis.DataSet([
        {id: 1, label: 'Node 1'},
        {id: 2, label: 'Node 2'},
        {id: 3, label: 'Node 3'},
        {id: 4, label: 'Node 4'},
        {id: 5, label: 'Node 5'}
    ]);

    // create an array with edges
    var edges = new vis.DataSet([
        {from: 1, to: 3},
        {from: 1, to: 2},
        {from: 2, to: 4},
        {from: 2, to: 5}
    ]);

    // create a network
    var container = document.getElementById(loc);

    // provide the data in the vis format
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {};

    // initialize your network!
    var network = new vis.Network(container, data, options);

}


function draw(where) {
    var canvas = document.getElementById(where);

    if (canvas.getContext) {
        var ctx = canvas.getContext("2d");

        ctx.fillStyle = "rgb(200,0,0)";
        ctx.fillRect(10, 10, 55, 50);

        ctx.fillStyle = "rgba(0,0,200,0.5)";
        ctx.fillRect(30, 30, 55, 50);
    } else {
        alert("Canvas isn't supported.");
    }
}

function test_jsnetworkx(){
    var G = new jsnx.DiGraph();

    G.addNodesFrom([1,2,3,4,5,[9,{color: '#008A00'}]], {color: '#0064C7'});
    G.addCycle([1,2,3,4,5]);
    G.addEdgesFrom([[1,9], [9,1]]);

    jsnx.draw(G, {
        element: '#ch_canvas',
        withLabels: true,
        nodeStyle: {
            fill: function(d) {
                return d.data.color;
            }
        },
        labelStyle: {fill: 'white'},
        stickyDrag: true
    });

}

function test_jsnetworkx1(){
    var G = new jsnx.Graph();

    G.addNodesFrom([1,2,3,4], {group:0});
    G.addNodesFrom([5,6,7], {group:1});
    G.addNodesFrom([8,9,10,11], {group:2});

    G.addPath([1,2,5,6,7,8,11]);
    G.addEdgesFrom([[1,3],[1,4],[3,4],[2,3],[2,4],[8,9],[8,10],[9,10],[11,10],[11,9]]);

    var color = d3.scale.category20();
    jsnx.draw(G, {
        element: '#ch_canvas',
        layoutAttr: {
            charge: -120,
            linkDistance: 20
        },
        nodeAttr: {
            r: 5,
            title: function(d) { return d.label;}
        },
        nodeStyle: {
            fill: function(d) {
                return color(d.data.group);
            },
            stroke: 'none'
        },
        edgeStyle: {
            fill: '#999'
        }
    });
}