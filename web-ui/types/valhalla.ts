// Valhalla API Type Definitions

export type CostingType = 'auto' | 'bicycle' | 'pedestrian' | 'truck' | 'bus' | 'taxi';

export interface Location {
  lat: number;
  lon: number;
  type?: 'break' | 'through' | 'via' | 'break_through';
  heading?: number;
  heading_tolerance?: number;
  minimum_reachability?: number;
  radius?: number;
  rank_candidates?: boolean;
  preferred_side?: 'same' | 'opposite' | 'either';
  display_lat?: number;
  display_lon?: number;
  street_side_tolerance?: number;
  street_side_max_distance?: number;
}

export interface AutoCostingOptions {
  maneuver_penalty?: number;
  destination_only_penalty?: number;
  gate_cost?: number;
  gate_penalty?: number;
  toll_booth_cost?: number;
  toll_booth_penalty?: number;
  ferry_cost?: number;
  use_ferry?: number;
  use_highways?: number;
  use_tolls?: number;
  use_tracks?: number;
  use_living_streets?: number;
  use_lit?: number;
  private_access_penalty?: number;
  ignore_access?: boolean;
  ignore_closures?: boolean;
  ignore_restrictions?: boolean;
  ignore_oneways?: boolean;
  height?: number;
  width?: number;
}

export interface BicycleCostingOptions {
  maneuver_penalty?: number;
  destination_only_penalty?: number;
  gate_cost?: number;
  gate_penalty?: number;
  toll_booth_cost?: number;
  toll_booth_penalty?: number;
  ferry_cost?: number;
  use_roads?: number;
  use_tracks?: number;
  use_hills?: number;
  use_ferry?: number;
  use_living_streets?: number;
  use_lit?: number;
  bicycle_type?: 'Road' | 'Cross' | 'Hybrid' | 'Mountain';
  cycling_speed?: number;
  use_paths?: number;
}

export interface PedestrianCostingOptions {
  maneuver_penalty?: number;
  destination_only_penalty?: number;
  gate_cost?: number;
  gate_penalty?: number;
  toll_booth_cost?: number;
  toll_booth_penalty?: number;
  ferry_cost?: number;
  use_ferry?: number;
  use_roads?: number;
  use_tracks?: number;
  use_living_streets?: number;
  use_lit?: number;
  walking_speed?: number;
  walkway_factor?: number;
  sidewalk_factor?: number;
  alley_factor?: number;
  driveway_factor?: number;
  step_penalty?: number;
  max_grade?: number;
  ignore_access?: boolean;
  ignore_closures?: boolean;
  ignore_restrictions?: boolean;
}

export interface TruckCostingOptions {
  maneuver_penalty?: number;
  destination_only_penalty?: number;
  gate_cost?: number;
  gate_penalty?: number;
  toll_booth_cost?: number;
  toll_booth_penalty?: number;
  ferry_cost?: number;
  use_ferry?: number;
  use_highways?: number;
  use_tolls?: number;
  use_tracks?: number;
  use_living_streets?: number;
  use_lit?: number;
  height?: number;
  width?: number;
  weight?: number;
  axle_load?: number;
  hazmat?: boolean;
  private_access_penalty?: number;
  ignore_access?: boolean;
  ignore_closures?: boolean;
  ignore_restrictions?: boolean;
}

export type CostingOptions = 
  | { auto?: AutoCostingOptions }
  | { bicycle?: BicycleCostingOptions }
  | { pedestrian?: PedestrianCostingOptions }
  | { truck?: TruckCostingOptions };

export interface RouteRequest {
  locations: Location[];
  costing: CostingType;
  costing_options?: CostingOptions;
  directions_options?: {
    units?: 'kilometers' | 'miles';
    directions_type?: 'none' | 'maneuvers' | 'instructions';
    format?: 'text' | 'html';
  };
  exclude_locations?: Location[];
  exclude_polygons?: Array<Array<[number, number]>>;
  shape_match?: 'edge_walk' | 'map_snap' | 'walk_or_snap';
  filters?: {
    attributes?: string[];
    filters?: Record<string, unknown>;
  };
  shape?: Array<[number, number]>;
  alternate?: number;
  exclude_unpaved?: boolean;
  exclude_tolls?: boolean;
  exclude_highways?: boolean;
  exclude_ferry?: boolean;
  date_time?: {
    type: number;
    value: string;
  };
  shape_format?: 'polyline5' | 'polyline6';
  filters_action?: 'include' | 'exclude';
}

export interface RouteManeuver {
  type: number;
  instruction: string;
  verbal_succinct_transition_instruction?: string;
  verbal_pre_transition_instruction?: string;
  verbal_post_transition_instruction?: string;
  street_names?: string[];
  time: number;
  length: number;
  begin_shape_index: number;
  end_shape_index: number;
  toll?: boolean;
  rough?: boolean;
  gate?: boolean;
  ferry?: boolean;
  sign?: {
    exit_number?: string[];
    exit_branch?: string[];
    exit_toward?: string[];
    exit_name?: string[];
  };
  roundabout_exit_count?: number;
  depart_instruction?: number;
  verbal_depart_instruction?: string;
  arrive_instruction?: number;
  verbal_arrive_instruction?: string;
  transit_info?: unknown;
  verbal_multi_cue?: boolean;
  travel_mode?: string;
  travel_type?: string;
}

export interface RouteLeg {
  maneuvers: RouteManeuver[];
  shape: string;
  summary: {
    has_time_restrictions: boolean;
    has_toll: boolean;
    has_highway: boolean;
    has_ferry: boolean;
    min_lat: number;
    min_lon: number;
    max_lat: number;
    max_lon: number;
    time: number;
    length: number;
    cost: number;
  };
}

export interface RouteTrip {
  locations: Location[];
  legs: RouteLeg[];
  summary: {
    has_time_restrictions: boolean;
    has_toll: boolean;
    has_highway: boolean;
    has_ferry: boolean;
    min_lat: number;
    min_lon: number;
    max_lat: number;
    max_lon: number;
    time: number;
    length: number;
    cost: number;
  };
  status_message: string;
  status: number;
  units: string;
  language: string;
}

export interface RouteResponse {
  trip: RouteTrip;
  id?: string;
}

export interface IsochroneRequest {
  locations: Location[];
  costing: CostingType;
  costing_options?: CostingOptions;
  contours: Array<{
    time?: number;
    distance?: number;
    color?: string;
  }>;
  polygons?: boolean;
  denoise?: number;
  generalize?: number;
  show_locations?: boolean;
  date_time?: {
    type: number;
    value: string;
  };
}

export interface IsochroneContour {
  geometry: {
    type: 'Polygon';
    coordinates: Array<Array<[number, number]>>;
  };
  color?: string;
}

export interface IsochroneFeature {
  type: 'Feature';
  geometry: {
    type: 'Polygon';
    coordinates: Array<Array<[number, number]>>;
  };
  properties: {
    color?: string;
    contour?: number;
    metric?: number;
    [key: string]: unknown;
  };
}

export interface IsochroneResponse {
  type: 'FeatureCollection';
  features: IsochroneFeature[];
}

export interface MatrixRequest {
  sources: Location[];
  targets: Location[];
  costing: CostingType;
  costing_options?: CostingOptions;
  shape_match?: 'edge_walk' | 'map_snap' | 'walk_or_snap';
  date_time?: {
    type: number;
    value: string;
  };
  sources_to_targets?: Array<{
    from_index?: number;
    to_index?: number;
  }>;
}

export interface MatrixElement {
  from_index: number;
  to_index: number;
  distance: number;
  time: number;
  date_time?: number;
  to_leg_distance?: number;
  to_leg_duration?: number;
}

export interface MatrixResponse {
  sources: Array<{
    lat: number;
    lon: number;
  }>;
  targets: Array<{
    lat: number;
    lon: number;
  }>;
  sources_to_targets: Array<Array<MatrixElement>>;
  units: string;
}

export interface ValhallaError {
  error: number;
  error_code: number;
  error_message: string;
  status_code: number;
  status: string;
}
