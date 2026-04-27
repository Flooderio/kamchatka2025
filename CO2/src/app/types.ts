export interface TripData {
  flightDistance: number;
  flightClass: 'economy' | 'business';
  groundTransport: 'car' | 'bus' | 'train' | 'none';
  groundDistance: number;
  accommodation: 'hotel' | 'hostel' | 'ecolodge' | 'camping';
  nights: number;
  activities: string[];
  diet: 'meat' | 'mixed' | 'vegetarian' | 'vegan';
}

export interface CO2Results {
  total: number;
  breakdown: {
    transportation: number;
    accommodation: number;
    activities: number;
    food: number;
  };
  equivalents: {
    trees: number;
    cars: number;
    flights: number;
  };
}
