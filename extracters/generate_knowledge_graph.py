import json

def generate_knowledge_graph_html(subgraph_data, questions_data, output_html="knowledge_graph.html"):
    """
    1) 小球半径=54(原36的1.5倍)
    2) 词语间距增大: link distance=200, charge strength=-400
    3) 搜索匹配成功 => 小球背景变红, 否则恢复skyblue
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Knowledge Graph</title>
    <style>
        body {{
            margin: 0; 
            padding: 0;
            font-family: sans-serif;
        }}
        /* 顶部搜索框 */
        #searchBar {{
            position: absolute;
            top: 0;
            width: 100vw;
            height: 8vh;
            background-color: #f1f1f1; 
            text-align: center; 
            line-height: 10vh;
            z-index: 10000;
        }}
        #searchInput {{
            font-size: 25px;
            width: 50%;
            height: 30px;
        }}

        /* 图容器(其余9/10) */
        #graph {{
            position: absolute;
            top: 10vh;
            width: 100vw;
            height: 90vh;
        }}

        /* 关系: 浅棕色 */
        .link {{
            stroke-opacity: 0.6;
        }}
        /* 词语: 初始背景 skyblue，半径=54 */
        .node-circle {{
            cursor: pointer;
            stroke: #fff;
            stroke-width: 1.5px;
            fill: skyblue; 
        }}
        /* 词语文字: 24px黑色 */
        .node-label {{
            cursor: pointer;
            font-size: 24px; 
            font-weight: bold;
            fill: #000;  
            user-select: none;
        }}

        /* 弹窗3/4占比,字号48px */
        #infoBox {{
            position: absolute;
            width: 75vw;           
            height: 75vh;          
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            border: 1px solid #ccc;
            background-color: #fff;
            padding: 20px;
            display: none;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
            z-index: 9999;
            overflow-y: auto;
            font-size: 18px;   
        }}
        #infoTitle {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        #closeBtn {{
            float: right;
            cursor: pointer;
            color: #aaa;
            font-size: 32px;
        }}
        #closeBtn:hover {{
            color: #000;
        }}
        .analysis-toggle {{
            font-size: 20px;
            margin-top: 10px;
            cursor: pointer;
            background-color: #ddd;
            border: none;
            padding: 4px 8px;
        }}
        .analysis-content {{
            display: none;
            margin: 10px 0;
        }}
    </style>
</head>
<body>

    <!-- 顶部搜索框 -->
    <div id="searchBar">
        <input type="text" id="searchInput" placeholder="输入关键字搜索词语..." />
    </div>

    <div id="graph"></div>

    <div id="infoBox">
        <div id="closeBtn">[关闭]</div>
        <div id="infoTitle"></div>
        <div id="infoContent"></div>
    </div>

    <!-- D3.js -->
    <script src="https://d3js.org/d3.v6.min.js"></script>

    <script>
    // 1. 载入数据
    var graphData = {{
        "nodes": {json.dumps(subgraph_data["nodes"], ensure_ascii=False)},
        "edges": {json.dumps(subgraph_data["edges"], ensure_ascii=False)},
        "questions": {json.dumps(questions_data, ensure_ascii=False)}
    }};

    var container = document.getElementById("graph");
    var width = container.clientWidth;
    var height = container.clientHeight;

    // 2. 设置缩放 & 力导向(加大间距)
    var zoom = d3.zoom().on("zoom", function(event) {{
        svg.attr("transform", event.transform);
    }});

    var svg = d3.select("#graph").append("svg")
        .attr("width", width)
        .attr("height", height)
        .call(zoom)
        .append("g");

    // forceLink.distance(200) => 加大词语间距离
    // forceManyBody.strength(-400) => 增加排斥力, 让词语分布更开

    // 关系颜色=浅棕(#DEB887), 粗细 range(2~15)
    var maxWeight = d3.max(graphData.edges, function(e) {{return e.weight;}});
    var scaleStroke = d3.scaleLinear().domain([0, maxWeight]).range([2,15]);

    var simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.edges)
            .id(function(d) {{ return d.id; }})
            .distance(200)
        )
        .force("charge", d3.forceManyBody().strength(-400))
        .force("center", d3.forceCenter(width/2, height/2));

    var link = svg.selectAll(".link")
        .data(graphData.edges)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke", "#DEB887")
        .attr("stroke-width", function(d) {{
            return scaleStroke(d.weight);
        }})
        .on("click", function(event, d) {{
            event.stopPropagation();
            showEdgeInfo(d);
        }});

    // 3. 绘制词语(小球半径=54)
    var nodeGroup = svg.selectAll(".node-group")
        .data(graphData.nodes)
        .enter().append("g")
        .attr("class", "node-group")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("click", function(event, d) {{
            event.stopPropagation();
            showNodeInfo(d);
        }});

    nodeGroup.append("circle")
        .attr("class", "node-circle")
        .attr("r", 54);

    nodeGroup.append("text")
        .attr("class", "node-label")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .text(function(d) {{ return d.id; }});

    simulation.on("tick", function() {{
        link
            .attr("x1", function(d) {{ return d.source.x; }})
            .attr("y1", function(d) {{ return d.source.y; }})
            .attr("x2", function(d) {{ return d.target.x; }})
            .attr("y2", function(d) {{ return d.target.y; }});

        nodeGroup.attr("transform", function(d) {{
            return "translate(" + d.x + "," + d.y + ")";
        }});
    }});

    function dragstarted(event, d) {{
        if(!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }}
    function dragged(event, d) {{
        d.fx = event.x;
        d.fy = event.y;
    }}
    function dragended(event, d) {{
        if(!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }}

    // 4. 实时搜索 => 匹配成功 => 小球背景变红，否则保持skyblue
    var searchInput = document.getElementById("searchInput");
    searchInput.addEventListener("input", function(evt) {{
        var keyword = searchInput.value.trim().toLowerCase();
        // 若输入为空 => 恢复全部skyblue
        if(!keyword) {{
            nodeGroup.select("circle").attr("fill", "skyblue");
            return;
        }}

        // 找出匹配的词语
        var matchedNodes = [];
        graphData.nodes.forEach(function(n) {{
            if(n.id.toLowerCase().indexOf(keyword) !== -1) {{
                matchedNodes.push(n);
            }}
        }});

        // 先全部恢复 skyblue
        nodeGroup.select("circle").attr("fill", "skyblue");

        if(matchedNodes.length === 0) {{
            // 无匹配 => 不居中不提示
            return;
        }}

        // 把匹配到的词语 circle 改成红色
        nodeGroup.each(function(d) {{
            if(matchedNodes.indexOf(d) !== -1) {{
                d3.select(this).select("circle").attr("fill", "red");
            }}
        }});

        // 若仅匹配1个 => 定位缩放
        if(matchedNodes.length === 1) {{
            centerNode(matchedNodes[0]);
        }}
    }});

    function centerNode(d) {{
        var scale = 2; // 放大倍数
        var x = d.x;
        var y = d.y;
        var translateX = width/2 - x*scale;
        var translateY = height/2 - y*scale;

        svg.transition()
           .duration(750)
           .call( 
               zoom.transform, 
               d3.zoomIdentity.translate(translateX, translateY).scale(scale)
           );
    }}

    // 5. 点击空白 => 关闭弹窗
    d3.select("body").on("click", function() {{
        hideInfoBox();
    }});

    // 6. 弹窗 & 折叠解析
    var infoBox = document.getElementById("infoBox");
    var infoTitle = document.getElementById("infoTitle");
    var infoContent = document.getElementById("infoContent");
    var closeBtn = document.getElementById("closeBtn");

    function showNodeInfo(nodeData) {{
        var title = "词语: " + nodeData.id;
        var content = "<p><strong>解释：</strong> " + (nodeData.explanation || "") + "</p>";
        if(nodeData.similar && nodeData.similar.length > 0) {{
            content += "<p><strong>相似词：</strong> " + nodeData.similar.join('、') + "</p>";
        }}
        if(nodeData.opposite && nodeData.opposite.length > 0) {{
            content += "<p><strong>反义词：</strong> " + nodeData.opposite.join('、') + "</p>";
        }}
        showInfoBox(title, content);
    }}

    function showEdgeInfo(edgeData) {{
        var title = "关系: " + edgeData.source.id + " -- " + edgeData.target.id;
        var content = "<p><strong>考场上共同出现的次数：</strong> " + edgeData.weight + "</p>";
        if(edgeData.questions && edgeData.questions.length > 0) {{
            content += "<p><strong>共考题号：</strong> " + edgeData.questions.join('、') + "</p>";
            content += "<hr/><p><strong>题目详情：</strong></p>";
            edgeData.questions.forEach(function(qid) {{
                var q = graphData.questions[qid];
                if(q) {{
                    content += "<div style='margin-bottom:8px;'>";
                    content += "<strong>题号 " + qid + "：</strong><br/>";
                    content += q.text + "<br/>";
                    if(q.options) {{
                        content += q.options.join("<br/>") + "<br/>";
                    }}
                    if(q.analysis) {{
                        content += "<button class='analysis-toggle' onclick='toggleAnalysis({{QID}}, event)'>展开/收起解析</button>"
                                   .replace("{{QID}}", qid);
                        content += "<div id='analysis-{{QID}}' class='analysis-content'>"
                                   .replace("{{QID}}", qid);
                        content += q.analysis + "</div>";
                    }}
                    content += "</div>";
                }} else {{
                    content += "【题号 " + qid + "】 未在题库中找到<br/>";
                }}
            }});
        }}
        showInfoBox(title, content);
    }}

    function showInfoBox(title, content) {{
        infoTitle.innerHTML = title;
        infoContent.innerHTML = content;
        infoBox.style.display = "block";
    }}
    function hideInfoBox() {{
        infoBox.style.display = "none";
    }}

    closeBtn.addEventListener("click", function(evt) {{
        hideInfoBox();
        evt.stopPropagation();
    }});

    function toggleAnalysis(qid, ev) {{
        ev.stopPropagation();
        var el = document.getElementById("analysis-" + qid);
        if(!el) return;
        if(el.style.display === "none" || el.style.display === "") {{
            el.style.display = "block";
        }} else {{
            el.style.display = "none";
        }}
    }}
    window.toggleAnalysis = toggleAnalysis;
    </script>
</body>
</html>
"""
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"新的知识图谱已生成: {output_html}")


def main():
    # 1. 读取 large_subgraph_2.json
    with open("large_subgraph_11.json", "r", encoding="utf-8") as f:
        subgraph_data = json.load(f)

    # 2. 读取 merged_questions.json
    with open("merged_questions.json", "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    # 3. 生成 HTML
    generate_knowledge_graph_html(subgraph_data, questions_data, "knowledge_graph_11.html")


if __name__ == "__main__":
    main()
