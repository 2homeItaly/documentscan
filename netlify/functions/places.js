import fetch from 'node-fetch';

/**
 * Netlify Serverless Function: Restaurant Finder
 *
 * Finds and categorizes restaurants near a given address using:
 * - Nominatim API for geocoding (free)
 * - Overpass API for POI data (free)
 *
 * Usage: /.netlify/functions/places?address=Via+Sparano+Bari
 */

// Constants
const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search';
const OVERPASS_URL = 'https://overpass-api.de/api/interpreter';
const SEARCH_RADIUS = 1500; // meters
const USER_AGENT = 'RestaurantFinder/1.0';

// Restaurant categories with keywords
const CATEGORIES = {
  pasta: {
    keywords: ['pasta', 'italian', 'trattoria', 'osteria', 'cucina italiana'],
    cuisines: ['italian', 'pasta'],
    tags: ['pasta', 'trattoria', 'italian_restaurant']
  },
  fish: {
    keywords: ['fish', 'seafood', 'pesce', 'mare', 'seafood'],
    cuisines: ['seafood', 'fish'],
    tags: ['seafood', 'fish', 'pescatore']
  },
  meat: {
    keywords: ['steak', 'grill', 'carne', 'bbq', 'churrascaria', 'barbecue'],
    cuisines: ['steakhouse', 'barbecue', 'grill'],
    tags: ['steak_house', 'grill', 'bbq']
  },
  pizza: {
    keywords: ['pizza', 'pizzeria', 'napoletana'],
    cuisines: ['pizza'],
    tags: ['pizzeria', 'pizza']
  },
  other: {
    keywords: ['american', 'mexican', 'vegetarian', 'vegan', 'asian', 'japanese', 'chinese', 'thai'],
    cuisines: ['american', 'mexican', 'vegetarian', 'vegan', 'asian', 'japanese', 'chinese', 'thai'],
    tags: ['burger', 'taco', 'vegetarian', 'vegan']
  }
};

/**
 * Geocode address using Nominatim
 */
async function geocodeAddress(address) {
  const url = `${NOMINATIM_URL}?q=${encodeURIComponent(address)}&format=json&limit=1`;

  const response = await fetch(url, {
    headers: {
      'User-Agent': USER_AGENT
    }
  });

  if (!response.ok) {
    throw new Error(`Nominatim API error: ${response.status}`);
  }

  const data = await response.json();

  if (!data || data.length === 0) {
    throw new Error('Address not found');
  }

  return {
    lat: parseFloat(data[0].lat),
    lon: parseFloat(data[0].lon),
    display_name: data[0].display_name
  };
}

/**
 * Query Overpass API for restaurants near coordinates
 */
async function findNearbyRestaurants(lat, lon, radius) {
  // Overpass QL query for restaurants, cafes, bars, fast_food
  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="restaurant"](around:${radius},${lat},${lon});
      node["amenity"="cafe"](around:${radius},${lat},${lon});
      node["amenity"="bar"](around:${radius},${lat},${lon});
      node["amenity"="fast_food"](around:${radius},${lat},${lon});
      way["amenity"="restaurant"](around:${radius},${lat},${lon});
      way["amenity"="cafe"](around:${radius},${lat},${lon});
      way["amenity"="bar"](around:${radius},${lat},${lon});
      way["amenity"="fast_food"](around:${radius},${lat},${lon});
    );
    out body;
    >;
    out skel qt;
  `;

  const response = await fetch(OVERPASS_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'User-Agent': USER_AGENT
    },
    body: `data=${encodeURIComponent(query)}`
  });

  if (!response.ok) {
    throw new Error(`Overpass API error: ${response.status}`);
  }

  const data = await response.json();
  return data.elements || [];
}

/**
 * Calculate match score for a restaurant against a category
 */
function calculateCategoryScore(restaurant, category) {
  let score = 0;
  const tags = restaurant.tags || {};

  // Check name
  const name = (tags.name || '').toLowerCase();
  category.keywords.forEach(keyword => {
    if (name.includes(keyword)) score += 3;
  });

  // Check cuisine
  const cuisine = (tags.cuisine || '').toLowerCase();
  category.cuisines.forEach(cuis => {
    if (cuisine.includes(cuis)) score += 5;
  });

  // Check description
  const description = (tags.description || '').toLowerCase();
  category.keywords.forEach(keyword => {
    if (description.includes(keyword)) score += 2;
  });

  // Bonus for specialty tags
  category.tags.forEach(tag => {
    if (tags[tag]) score += 4;
  });

  return score;
}

/**
 * Categorize restaurants into groups
 */
function categorizeRestaurants(restaurants) {
  const categorized = {
    pasta: [],
    fish: [],
    meat: [],
    pizza: [],
    other: []
  };

  // Remove duplicates by name
  const uniqueRestaurants = [];
  const seenNames = new Set();

  restaurants.forEach(r => {
    const name = r.tags?.name || 'Unknown';
    if (!seenNames.has(name.toLowerCase())) {
      seenNames.add(name.toLowerCase());
      uniqueRestaurants.push(r);
    }
  });

  // Score each restaurant for each category
  uniqueRestaurants.forEach(restaurant => {
    const scores = {};
    let maxScore = 0;
    let bestCategory = 'other';

    // Calculate scores for each category
    Object.keys(CATEGORIES).forEach(catName => {
      const score = calculateCategoryScore(restaurant, CATEGORIES[catName]);
      scores[catName] = score;

      if (score > maxScore) {
        maxScore = score;
        bestCategory = catName;
      }
    });

    // Only assign if score > 0, otherwise it goes to 'other'
    if (maxScore === 0) {
      bestCategory = 'other';
    }

    // Format restaurant data
    const formatted = {
      name: restaurant.tags?.name || 'Unknown Restaurant',
      cuisine: restaurant.tags?.cuisine || 'Not specified',
      amenity: restaurant.tags?.amenity || 'restaurant',
      address: formatAddress(restaurant.tags),
      lat: restaurant.lat,
      lon: restaurant.lon,
      score: maxScore,
      tags: restaurant.tags
    };

    categorized[bestCategory].push(formatted);
  });

  // Sort each category by score (descending) and limit to top 3
  Object.keys(categorized).forEach(category => {
    categorized[category] = categorized[category]
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
  });

  return categorized;
}

/**
 * Format address from tags
 */
function formatAddress(tags) {
  if (!tags) return 'Address not available';

  const parts = [];
  if (tags['addr:street']) parts.push(tags['addr:street']);
  if (tags['addr:housenumber']) parts.push(tags['addr:housenumber']);
  if (tags['addr:city']) parts.push(tags['addr:city']);
  if (tags['addr:postcode']) parts.push(tags['addr:postcode']);

  return parts.length > 0 ? parts.join(', ') : 'Address not available';
}

/**
 * Main Netlify Function Handler
 */
export async function handler(event, context) {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Handle OPTIONS request for CORS
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    // Get address from query parameters
    const address = event.queryStringParameters?.address;

    if (!address) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          error: 'Missing required parameter: address',
          usage: '/.netlify/functions/places?address=Via+Sparano+Bari'
        })
      };
    }

    console.log(`Processing request for address: ${address}`);

    // Step 1: Geocode the address
    const location = await geocodeAddress(address);
    console.log(`Geocoded to: ${location.lat}, ${location.lon}`);

    // Step 2: Find nearby restaurants
    const restaurants = await findNearbyRestaurants(location.lat, location.lon, SEARCH_RADIUS);
    console.log(`Found ${restaurants.length} POIs`);

    // Step 3: Categorize restaurants
    const categorized = categorizeRestaurants(restaurants);

    // Step 4: Return response
    const response = {
      address: address,
      geocoded_address: location.display_name,
      center: {
        lat: location.lat,
        lon: location.lon
      },
      search_radius_meters: SEARCH_RADIUS,
      total_found: restaurants.length,
      categories: categorized,
      // Legacy format compatibility
      pasta: categorized.pasta,
      fish: categorized.fish,
      meat: categorized.meat,
      pizza: categorized.pizza,
      other: categorized.other
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(response, null, 2)
    };

  } catch (error) {
    console.error('Error:', error);

    // Determine error type and status code
    let statusCode = 500;
    let errorMessage = error.message;

    if (error.message.includes('Address not found')) {
      statusCode = 404;
    } else if (error.message.includes('API error')) {
      statusCode = 502;
    }

    return {
      statusCode,
      headers,
      body: JSON.stringify({
        error: errorMessage,
        timestamp: new Date().toISOString()
      })
    };
  }
}
