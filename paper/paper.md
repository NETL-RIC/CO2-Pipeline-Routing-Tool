---
title: A Geospatial Machine Learning Tool for Strategic CO2 Transport Planning  
tags:
    - Python
    - Javascript
    - Flask
    - React
    - Carbon Storage
    - Carbon Capture
    - CO2 Pipelines
authors:   
    - name: Stephen Leveckis
    affiliation: "1, 2"
    - name:  Benjamin Houghton
    - affiliation: "1, 2"
    - name: Dakota Zaengle
    - affiliation: "1, 2"
    - name: Michael C. Gao
    affiliation: "1, 2"
    - name: Catherine Schooley
    affiliation: "1, 2"
    - name: Jennifer R. Bauer
    affiliation: 1
    - name: Lucy Romeo
    affiliation: 1
affiliations:  
    -name: National Energy Technology Laboratory, 1450 Queen Avenue SW, Albany, OR 97321, USA  
    index: 1
    - name: NETL Support Contractor, 1450 Queen Avenue SW, Albany, OR 97321, USA  
    index: 2
---

# Summary  

Leading advancements in energy transportation planning and development, the U.S. Department of Energy’s (DOE) National Energy Technology Laboratory (NETL) has developed the Smart CO2 Transport Planning Tool (Leveckis et al., 2024). This geospatially driven, machine learning-informed tool enables users to identify potential new routes for pipelines and railways, as well as evaluate existing transportation routes for CO2 across the contiguous U.S. and Alaska. The tool is underpinned by a comprehensive spatial database representing a range of carbon transport planning and development criteria and considerations (Schooley et al. 2024), which informs the tool in both Identification and Evaluation Mode.  

# Statement of Need  

The Smart CO2 Transport Planning Tool (Leveckis et al., 2024) provides an interface to address the factors of carbon transport planning and development for researchers and industry professionals in carbon capture and storage. The considerations such as whether to use existing infrastructure, consideration of land use, or resource management (Ho et al 2024; Muhlbauer and Murrary, 2024) are difficult to ascertain and catalog without the assistance the tool provides given prospective pipeline data. To meet the next three decades of anticipated growth, U.S. pipeline infrastructure would need to expand by more than 100,000% (Larson et al., 2020), and no existing tools are available to support the comprehensive analyses needed to effectively plan and develop these transportation routes under these different considerations to meet growth demand. Novel to this tool, is the geospatial informational insights output, provided as a PDF report, that is determined by machine learning weighting over 60 different layers that help the algorithm evaluate consequences and considerations (Schooley et al., 2024) from either an existing route, or from a prospective one given a start and end destination. The tool renders all accepted data in the interactive map-based user interface (UI), built for intermodal use between route evaluation or identification to aid users in planning infrastructure for carbon storage or other energy transportation needs.   

# Software Features  

There are two main modes of operation for the tool, Evaluate Mode and Identification Mode. Evaluate Mode accepts a user input route, represented as a polyline in a shapefile (geospatial data format) uploaded through the UI from the user’s local storage. Identification Mode has two sub-modes, Route Mode and Rail Mode. Both require a user to provide a start and end destination and chose which mode to use. When Rail sub-mode is selected, users can designate whether to prioritize to use existing railways as a transportation method. When Route sub-mode is selected, the tool will not consider these railways and existing transportation infrastructures. The start and destination can be input and rendered with markers by clicking on the built-in map, entering coordinates in World Geodetic System 1983 (WGS 84) or selecting a location from a dropdown of known carbon capture and storage projects. Use of either mode will draw the supplied or presented transportation route on the map and provide a detailed PDF report using the map layer database created to communicate the routes’ interaction and crossing with these data layers. Using Identification Mode will create a potential pipeline route through machine learning and the map layer database to create an optimal route that reduces various costs, like those associated with considerations of existing regulations and requirements, as well as design or operational considerations that would impact the cost of development or effect the timeline of development. The tool itself can be downloaded as a standalone .exe, executing the server code and the user’s native browser for the UI.  

# Machine Learning Utilization  

The server code uses a Monte Carlo Tree Search (MCTS) algorithm for its ability to explore multidimensional search spaces while balancing total distance traveled with traversal of high-cost areas. Costs are parsed from the supporting layers in the spatial database, each layer gridded to a cell size of 10 km to cover the landmass of the U.S.  

# Supporting Database  

The Smart CO2 Transport Planning tool is geospatially informed by a spatial database that contains more than 60 weighted layers representing best practices, pipeline construction considerations, legislation, and other critical factors that influence the possibility of energy transportation development via pipeline or rail (Schooley et al., 2024). Layers, including land use, high consequence areas, slope, and soil properties are weighted on a normalized scale (0–1), where one represents development challenges and zero represents none. For tool parsing, they are summarized into a 10 km2 multivariate layer and a Census Tract multivariate layer spanning the contiguous U.S. and Alaska. The database is available on Energy Data eXchange® (EDX) (Schooley et al., 2025).  

# Lessons Learned   

Electron was unnecessary for packaging the UI as running React code in the browser was more lightweight and responsive. Proximal Policy Optimization (PPO) and Deep-Q Networks (DQN) were inefficient algorithms for the scale of the problems the tool aims to solve, and MCTS was chosen for its consideration of future possibilities and long-term tradeoffs.   

# Disclaimer 

This project was funded by the United States Department of Energy, National Energy Technology Laboratory, in part, through a site support contract. Neither the United States Government nor any agency thereof, nor any of their employees, nor the support contractor, nor any of their employees, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness of any information, apparatus, product, or process disclosed, or represents that its use would not infringe privately owned rights. Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United States Government or any agency thereof. The views and opinions of authors expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof. 

# References  

Ho, A., Giannopoulos, D., Pilorgé, H. and Psarras, P., 2024. Opportunities for rail in the transport of carbon dioxide in the United States. Frontiers in Energy Research, 11, p.1343085. https://link.springer.com/referenceworkentry/10.1007/978-3-031-33328-6_23   

Larson, E., Greig, C., Jenkins, J., Mayfield, E., Pascale, A., Zhang, C., Drossman, J., Williams, R., Pacala, S., Socolow, R., Baik, E., Birdsey, R., Duke, R., Jones, R., Haley, B., Leslie, E., Paustian, K., and Swan A., 2020. NetZero America: Potential Pathways, Infrastructure, and Impacts Report, Princeton University.  

Leveckis, S., Houghton, B., Gao, M.C., Zaengle, D., Bauer, J., Rose, K., and Romeo, L., Smart CO2 Transport-Route Planning Tool, 7/31/2024, https://edx.netl.doe.gov/dataset/smart-co2-transport-route-planning-tool, DOI: 10.18141/2505034    

Ma, Z., B. Chen, and R. J. Pawar. "Reuse of Existing CO2 Pipeline and Pipeline Rights-Of-Way for Large-Scale CCS Deployments." In SPE Annual Technical Conference and Exhibition?, p. D021S030R001. SPE, 2024.  

Morgan, D., Sheriff, A. and Shih, C.Y., 2024. FECM/NETL CO2 Transport Cost Model (2024): Description and User’s Manual (No. DOE/NETL-2024/4860). National Energy Technology Laboratory (NETL), Pittsburgh, PA, Morgantown, WV, and Albany, OR (United States).  

Muhlbauer, W.K. and Murray, J., 2024. Pipeline Risk Management. In Handbook of Pipeline Engineering (pp. 939-957). Cham: Springer International Publishing. https://link.springer.com/referenceworkentry/10.1007/978-3-031-33328-6_23   

Schooley, C., Romeo, L., Pfander, I., Sharma, M., Justman, D., Bauer, J. and Rose, K., 2024. A curated data resource to support safe carbon dioxide transport-route planning. Data in Brief, 52, p.109984.  