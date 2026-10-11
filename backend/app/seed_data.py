"""
Seed data for the Ghaziabad stretch of Hindon River:
- River coordinates
- Drains & outfalls
- IoT Sensor Nodes
- Initial sample tickets and labeled images
"""

# Hindon River centerline in Ghaziabad (North to South flow)
HINDON_RIVER_COORDINATES = [
    [28.7125, 77.4010],  # Upstream entry (near Morti / Karhera north)
    [28.6942, 77.4085],  # Karhera Bridge / Hindon Airbase East
    [28.6810, 77.4120],  # Mohan Nagar railway bridge
    [28.6655, 77.4168],  # GT Road Bridge / Old Bus Stand reach
    [28.6580, 77.4190],  # Hindon Barrage / Arthala confluence
    [28.6430, 77.4050],  # Kanawani / Indirapuram green belt
    [28.6285, 77.4230],  # Chhijarsi / NH-24 (Delhi-Meerut Expressway)
    [28.6010, 77.4310],  # Sector 63 / Chhapraula reach
    [28.5820, 77.4380],  # Downstream exit towards Noida/Greater Noida
]

# Major Drains / Outfalls entering Hindon River in Ghaziabad
DRAINS_DATA = [
    {
        "id": "DRAIN-01",
        "name": "Sahibabad Industrial Drain",
        "lat": 28.6612,
        "lng": 77.4110,
        "type": "industrial_cluster",
        "flow_direction": "east",
        "typical_pollutants": ["heavy_metals", "electroplating_acids", "dyes", "toxic_foam_surfactants"],
        "catchment_area": "Sahibabad Site IV Industrial Area",
        "baseline_tds": 2100,
        "baseline_ph": 5.4,
        "regulatory_jurisdiction": "UPPCB (Pollution Control Board)",
        "upstream_rank_score": 0.95
    },
    {
        "id": "DRAIN-02",
        "name": "Dasna Slaughterhouse & Tannery Drain",
        "lat": 28.6820,
        "lng": 77.4250,
        "type": "meat_processing_tannery",
        "flow_direction": "south_west",
        "typical_pollutants": ["organic_sludge", "blood_effluent", "pathogens", "high_bod"],
        "catchment_area": "Dasna - Masuri Industrial Belt",
        "baseline_tds": 1850,
        "baseline_ph": 7.9,
        "regulatory_jurisdiction": "UPPCB (Pollution Control Board)",
        "upstream_rank_score": 0.88
    },
    {
        "id": "DRAIN-03",
        "name": "Karhera Municipal Outfall",
        "lat": 28.6945,
        "lng": 77.4095,
        "type": "municipal_sewage",
        "flow_direction": "south",
        "typical_pollutants": ["untreated_sewage", "single_use_plastics", "domestic_sludge"],
        "catchment_area": "Karhera & Nandgram Residential Wards",
        "baseline_tds": 850,
        "baseline_ph": 7.2,
        "regulatory_jurisdiction": "Nagar Nigam Ghaziabad",
        "upstream_rank_score": 0.75
    },
    {
        "id": "DRAIN-04",
        "name": "Arthala Mixed Drain",
        "lat": 28.6640,
        "lng": 77.4140,
        "type": "mixed_industrial_domestic",
        "flow_direction": "south_east",
        "typical_pollutants": ["detergents", "plastic_waste", "domestic_sewage"],
        "catchment_area": "Arthala & Mohan Nagar Mixed Sector",
        "baseline_tds": 1200,
        "baseline_ph": 6.8,
        "regulatory_jurisdiction": "UP Jal Nigam",
        "upstream_rank_score": 0.80
    },
    {
        "id": "DRAIN-05",
        "name": "Indirapuram STP Bypass Drain",
        "lat": 28.6390,
        "lng": 77.4010,
        "type": "stp_bypass",
        "flow_direction": "east",
        "typical_pollutants": ["raw_blackwater", "fecal_coliform", "nitrogen_spikes"],
        "catchment_area": "Indirapuram Housing Societies",
        "baseline_tds": 950,
        "baseline_ph": 7.1,
        "regulatory_jurisdiction": "UP Jal Nigam",
        "upstream_rank_score": 0.70
    },
    {
        "id": "DRAIN-06",
        "name": "Pratap Vihar Flood Plain Dumping Channel",
        "lat": 28.6520,
        "lng": 77.4280,
        "type": "solid_waste_channel",
        "flow_direction": "west",
        "typical_pollutants": ["construction_debris", "legacy_plastic", "burning_residue"],
        "catchment_area": "Pratap Vihar Embankment",
        "baseline_tds": 780,
        "baseline_ph": 7.4,
        "regulatory_jurisdiction": "UP Irrigation Department",
        "upstream_rank_score": 0.65
    }
]

# IoT Sensor Nodes placed strategically along the Hindon river
SENSOR_NODES_DATA = [
    {
        "node_id": "HIN-NODE-01",
        "node_name": "Karhera Upstream Sensor",
        "lat": 28.6940,
        "lng": 77.4080,
        "reach_km": 2.5,
        "description": "Baseline monitoring node upstream of Ghaziabad city center",
        "current": {
            "ph": 7.3,
            "turbidity_ntu": 42.0,
            "tds_ppm": 580.0,
            "temp_c": 26.2,
            "is_anomaly": False
        }
    },
    {
        "node_id": "HIN-NODE-02",
        "node_name": "Hindon Barrage Central Sensor",
        "lat": 28.6585,
        "lng": 77.4185,
        "reach_km": 7.8,
        "description": "Critical monitoring station near Barrage gates and Arthala confluence",
        "current": {
            "ph": 5.2,  # Acidic spike!
            "turbidity_ntu": 185.0,  # High turbidity!
            "tds_ppm": 2400.0,  # Industrial spike!
            "temp_c": 28.5,
            "is_anomaly": True,
            "anomaly_reason": "Severe chemical discharge with acidic pH and massive TDS spike"
        }
    },
    {
        "node_id": "HIN-NODE-03",
        "node_name": "Kanawani Culvert Sensor",
        "lat": 28.6410,
        "lng": 77.4045,
        "reach_km": 11.2,
        "description": "Downstream sensor monitoring Indirapuram & Sahibabad outfall reach",
        "current": {
            "ph": 6.8,
            "turbidity_ntu": 95.0,
            "tds_ppm": 1420.0,
            "temp_c": 27.1,
            "is_anomaly": False
        }
    },
    {
        "node_id": "HIN-NODE-04",
        "node_name": "Chhijarsi NH-24 Bridge Sensor",
        "lat": 28.6280,
        "lng": 77.4235,
        "reach_km": 14.6,
        "description": "Exit boundary node at NH-24 Delhi-Meerut Expressway",
        "current": {
            "ph": 7.1,
            "turbidity_ntu": 78.0,
            "tds_ppm": 1100.0,
            "temp_c": 26.8,
            "is_anomaly": False
        }
    }
]

# Sample Labeled Incidents / Tickets for initial state & testing
INITIAL_TICKETS = [
    {
        "id": "TKT-HIN-001",
        "created_at": "2026-10-10T08:30:00Z",
        "updated_at": "2026-10-10T09:15:00Z",
        "title": "Industrial Effluent & Toxic White Foam at Hindon Barrage",
        "description": "Downstream sensor HIN-NODE-02 registered TDS spike (2400 ppm) and pH 5.2. Severe foaming visible at Barrage weir.",
        "incident_type": "toxic_foam",
        "severity": "CRITICAL",
        "confidence": 0.96,
        "status": "DISPATCHED",
        "location": {
            "lat": 28.6585,
            "lng": 77.4185,
            "address": "Hindon Barrage Weir, GT Road Bypass, Ghaziabad",
            "reach_km": 7.8
        },
        "source_hypotheses": [
            {
                "source_id": "SRC-HYP-01",
                "name": "Sahibabad Industrial Area Drain 01",
                "drain_id": "DRAIN-01",
                "type": "industrial_cluster",
                "confidence": 0.89,
                "distance_upstream_m": 850.0,
                "evidence": [
                    "Flow direction vector correlates directly with Barrage intake",
                    "Chemical profile (TDS 2400 ppm, pH 5.2) matches Sahibabad electroplating & textile cluster",
                    "No rainfall in past 24 hrs rules out natural stormwater runoff"
                ]
            },
            {
                "source_id": "SRC-HYP-02",
                "name": "Arthala Mixed Drain 04",
                "drain_id": "DRAIN-04",
                "type": "mixed_industrial_domestic",
                "confidence": 0.54,
                "distance_upstream_m": 620.0,
                "evidence": [
                    "Confluence is within 1 km upstream",
                    "Lower chemical concentration historically compared to current spike magnitude"
                ]
            }
        ],
        "assigned_department": "UPPCB (Pollution Control Board)",
        "patrol_assignment": {
            "officer_name": "Er. R. K. Sharma (UPPCB Field Inspector)",
            "patrol_id": "PATROL-UPPCB-04",
            "dispatched_at": "2026-10-10T09:10:00Z",
            "target_eta": "2026-10-10T11:00:00Z",
            "route_order": 1
        },
        "before_photo_url": "https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&w=800&q=80",
        "before_photo_analysis": {
            "detected_objects": ["thick_chemical_foam", "discolored_turbid_water", "river_embankment"],
            "pollution_type": "toxic_foam",
            "severity_score": 9.2,
            "cleanliness_score": 12.0,
            "confidence": 0.95,
            "visual_evidence": [
                "Over 60% of water surface covered in dense industrial surfactant foam",
                "Blackish-brown water discoloration visible beneath froth"
            ]
        },
        "after_photo_url": None,
        "after_photo_analysis": None,
        "sensor_trigger": {
            "node_id": "HIN-NODE-02",
            "parameter": "TDS_and_pH",
            "spike_value": 2400.0,
            "threshold": 1200.0
        },
        "verification": None,
        "escalation_approved": False
    },
    {
        "id": "TKT-HIN-002",
        "created_at": "2026-10-10T07:15:00Z",
        "updated_at": "2026-10-10T10:00:00Z",
        "title": "Massive Municipal Plastic Dumping at Karhera Ghat Embankment",
        "description": "Citizen report of commercial tractor-trolleys dumping unsegregated solid plastic and vegetable market waste.",
        "incident_type": "garbage_dumping",
        "severity": "HIGH",
        "confidence": 0.92,
        "status": "PENDING_VERIFICATION",
        "location": {
            "lat": 28.6942,
            "lng": 77.4085,
            "address": "Karhera Ghat Riverbank, Near Airbase Perimeter, Ghaziabad",
            "reach_km": 2.6
        },
        "source_hypotheses": [
            {
                "source_id": "SRC-HYP-03",
                "name": "Nandgram Vegetable Market Truck Route",
                "drain_id": "DRAIN-03",
                "type": "illegal_dumping_route",
                "confidence": 0.91,
                "distance_upstream_m": 120.0,
                "evidence": [
                    "Direct road access without boundary wall",
                    "Historical hotspot for municipal unauthorized solid waste dumping"
                ]
            }
        ],
        "assigned_department": "Nagar Nigam Ghaziabad",
        "patrol_assignment": {
            "officer_name": "Sanitation Inspector Amit Verma",
            "patrol_id": "PATROL-NNG-12",
            "dispatched_at": "2026-10-10T07:45:00Z",
            "target_eta": "2026-10-10T09:30:00Z",
            "route_order": 2
        },
        "before_photo_url": "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=800&q=80",
        "before_photo_analysis": {
            "detected_objects": ["plastic_bottles", "polybags", "organic_refuse", "embankment_debris"],
            "pollution_type": "garbage_dumping",
            "severity_score": 7.8,
            "cleanliness_score": 22.0,
            "confidence": 0.94,
            "visual_evidence": ["Accumulated multi-layer non-biodegradable debris covering 45 sq meters of flood plain"]
        },
        "after_photo_url": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=80",
        "after_photo_analysis": {
            "detected_objects": ["cleared_riverbank", "soil", "clean_water_edge"],
            "pollution_type": "garbage_dumping",
            "severity_score": 1.2,
            "cleanliness_score": 88.5,
            "confidence": 0.92,
            "visual_evidence": ["Waste heaps cleared by earthmovers; clean riparian buffer exposed"]
        },
        "sensor_trigger": None,
        "verification": None,
        "escalation_approved": False
    },
    {
        "id": "TKT-HIN-003",
        "created_at": "2026-10-09T14:20:00Z",
        "updated_at": "2026-10-10T06:00:00Z",
        "title": "Illegal Encroachment & Debris Dumping on Floodplain",
        "description": "Unauthorized temporary sheds and debris filling in the active floodplain buffer zone near Pratap Vihar.",
        "incident_type": "encroachment",
        "severity": "MEDIUM",
        "confidence": 0.88,
        "status": "OPEN",
        "location": {
            "lat": 28.6520,
            "lng": 77.4280,
            "address": "Pratap Vihar Embankment Reach, Ghaziabad",
            "reach_km": 9.1
        },
        "source_hypotheses": [],
        "assigned_department": "UP Irrigation Department",
        "patrol_assignment": None,
        "before_photo_url": "https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=800&q=80",
        "before_photo_analysis": {
            "detected_objects": ["debris_mound", "temporary_sheds", "riverbank"],
            "pollution_type": "encroachment",
            "severity_score": 5.5,
            "cleanliness_score": 45.0,
            "confidence": 0.88,
            "visual_evidence": ["Unauthorized leveling of river buffer zone with construction waste"]
        },
        "after_photo_url": None,
        "after_photo_analysis": None,
        "sensor_trigger": None,
        "verification": None,
        "escalation_approved": False
    }
]
