import { Brand, StoreCategory, NewArrivalCollection, TrendingEdit, InStoreEvent } from '../types';

const HERO_AUTUMN_IMG = "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1400&q=80";
const WOMEN_IMG = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1000&q=80";
const MEN_IMG = "https://images.unsplash.com/photo-1617137968427-85924c800a22?auto=format&fit=crop&w=1000&q=80";
const BEAUTY_IMG = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=1000&q=80";
const ACCESSORIES_IMG = "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1000&q=80";
const GROUND_IMG = "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?auto=format&fit=crop&w=1200&q=80";
const FIRST_IMG = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80";
const SECOND_IMG = "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1200&q=80";
const THIRD_IMG = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=1200&q=80";

export const STORE_INFO = {
  name: "Shoppers Stop Flagship Store",
  location: "In-Store Wi-Fi • Ground to Third Floor",
  address: "In-Store Guest Wi-Fi Network (SS_Guest_HighSpeed)",
  wifiNetwork: "Shoppers_Stop_Free_WiFi",
  customerAssistanceDesk: "Ground Floor Main Atrium & Second Floor VIP Lounge",
};

export const NEW_ARRIVALS: NewArrivalCollection[] = [
  {
    id: 'women-autumn',
    title: "New Season Edit",
    subtitle: "Sophisticated prints, breezy silks & contemporary silhouettes",
    category: 'WOMEN',
    badge: "Just Landed",
    imageUrl: WOMEN_IMG,
    description: "Explore the new season arrival rack featuring handcrafted embroidery, designer Western wear, and runway-inspired casuals curated for modern elegance.",
    highlights: ["Designer Indo-Western Tunics", "Linen-Blend Blazers", "Monochrome Statement Dresses"],
    storeLocation: "Second Floor • Women's Fashion Section A",
  },
  {
    id: 'men-smart-casual',
    title: "Latest Styles",
    subtitle: "Tailored blazers, Oxford cottons & refined street-luxe",
    category: 'MEN',
    badge: "In-Store Special",
    imageUrl: MEN_IMG,
    description: "Upgrade your wardrobe with premium Italian-finish cottons, unstructured blazers, and lightweight linen shirts now available on First Floor racks.",
    highlights: ["Pure Linen Casual Shirts", "Flex-Tech Chinos", "Lightweight Summer Blazers"],
    storeLocation: "First Floor • Men's Fashion Section B",
  },
  {
    id: 'beauty-glowing',
    title: "New & Trending",
    subtitle: "Luxury fragrances, radiant skincare & festive palettes",
    category: 'BEAUTY',
    badge: "Exclusive Counter",
    imageUrl: BEAUTY_IMG,
    description: "Visit the main beauty atrium for live complimentary makeover consultations, new botanical serums, and limited-edition fragrance launches.",
    highlights: ["Complimentary Skin Assessment", "Limited Edition Lip Velvet", "Niche Unisex Eau de Parfums"],
    storeLocation: "Ground Floor • Beauty & Cosmetics Atrium",
  },
  {
    id: 'accessories-luxe',
    title: "Fresh Arrivals",
    subtitle: "Chronographs, leather totes & polarized statement eyewear",
    category: 'ACCESSORIES',
    badge: "Curated Showcase",
    imageUrl: ACCESSORIES_IMG,
    description: "From Swiss precision timepieces to handcrafted Italian leather accessories, discover hand-selected pieces on display.",
    highlights: ["Automatic Mechanical Watches", "RFID Leather Wallets & Crossbodies", "Designer Polarized Sunglasses"],
    storeLocation: "Ground Floor • Accessories Gallery",
  },
];

export const BRANDS: Brand[] = [
  {
    id: 'brand-levis',
    name: "LEVI'S",
    category: "Denim & Casualwear",
    level: "First Floor",
    section: "Men's & Women's Denim Studio",
    description: "Iconic 501 jeans, trucker jackets, and sustainable denim collections.",
    featured: true,
    popularItems: ["501 Original Fit", "Trucker Jackets", "Graphic Logo Tees"],
  },
  {
    id: 'brand-lakme',
    name: "LAKMÉ",
    category: "Beauty & Cosmetics",
    level: "Ground Floor",
    section: "Beauty & Cosmetics Atrium",
    description: "India's premier makeup & skincare formulations with complimentary touch-up booth.",
    featured: true,
    popularItems: ["9to5 Primer Matte", "Absolute Hydra Matte Lipsticks", "Vitamin C+ Serums"],
  },
  {
    id: 'brand-tommy',
    name: "TOMMY HILFIGER",
    category: "Premium Lifestyle",
    level: "First Floor",
    section: "Men's Premium Casuals",
    description: "Classic American cool prep wear, signature polo shirts, and smart casuals.",
    featured: true,
    popularItems: ["Signature Polo Shirts", "Monogram Backpacks", "Casual Oxford Shirts"],
  },
  {
    id: 'brand-mac',
    name: "M.A.C COSMETICS",
    category: "Luxury Beauty",
    level: "Ground Floor",
    section: "Beauty Counter 04",
    description: "Professional artistry makeup, Studio Fix foundations, and iconic lip shades.",
    featured: true,
    popularItems: ["Studio Fix Fluid", "Ruby Woo Matte Lipstick", "Fix+ Prep Spray"],
  },
  {
    id: 'brand-biba',
    name: "BIBA",
    category: "Ethnic & Fusion Wear",
    level: "Second Floor",
    section: "Ethnic Wear Pavilion",
    description: "Contemporary ethnic wear, designer Anarkali suits, and festive kurtas.",
    featured: true,
    popularItems: ["Anarkali Suit Sets", "Mix & Match Dupattas", "Silk Blend Tunics"],
  },
  {
    id: 'brand-jackjones',
    name: "JACK & JONES",
    category: "Men's Street & Casual",
    level: "First Floor",
    section: "Youth Fashion Zone",
    description: "Contemporary menswear, cargo pants, denim shorts, and graphic tees.",
    featured: false,
    popularItems: ["Slim Fit Chinos", "Graphic Streetwear", "Distressed Jeans"],
  },
  {
    id: 'brand-forevernew',
    name: "FOREVER NEW",
    category: "Women's Western",
    level: "Second Floor",
    section: "Premium Womenswear",
    description: "Melbourne-designed feminine silhouettes, evening gowns, and tailored coats.",
    featured: false,
    popularItems: ["Wrap Satin Dresses", "Structured Tailored Blazers", "Floral Day Dresses"],
  },
  {
    id: 'brand-casio',
    name: "CASIO & G-SHOCK",
    category: "Watches & Electronics",
    level: "Ground Floor",
    section: "Timepiece Gallery",
    description: "Rugged G-Shock timepieces, vintage digital classics, and Edifice solar series.",
    featured: false,
    popularItems: ["G-Shock GA-2100", "Vintage Gold Series", "Edifice Chronograph"],
  },
  {
    id: 'brand-rayban',
    name: "RAY-BAN",
    category: "Eyewear",
    level: "Ground Floor",
    section: "Accessories & Eyewear",
    description: "Timeless Aviators, Wayfarers, and Clubmaster frames with UV protection.",
    featured: false,
    popularItems: ["Classic Aviator RB3025", "Wayfarer Classic", "Round Metal Frames"],
  },
];

export const STORE_FLOOR_DIRECTORY: StoreCategory[] = [
  {
    id: 'floor-ground',
    name: "GROUND FLOOR",
    level: "Ground Floor",
    subtitle: "Beauty, Fragrances, Watches & Eyewear",
    subcategories: [
      "Beauty & Cosmetics Atrium",
      "Luxury Fragrances Bar",
      "Watches & Timepiece Gallery",
      "Sunglasses & Eyewear",
      "Designer Handbags & Small Leather Goods",
      "First Citizen VIP Guest Desk"
    ],
    aisle: "Aisles 1 – 8",
    imageUrl: GROUND_IMG,
  },
  {
    id: 'floor-level1',
    name: "FIRST FLOOR",
    level: "First Floor",
    subtitle: "Men's Fashion, Formalwear, Casuals & Denim Studio",
    subcategories: [
      "Men's Formal Suits & Tailoring",
      "Smart Casuals & Linen Lounge",
      "Denim Studio (Levi's, Pepe, Flying Machine)",
      "Men's Footwear & Leather Belts",
      "Activewear & Athleisure",
      "Men's Grooming Lounge"
    ],
    aisle: "Aisles 9 – 16",
    imageUrl: FIRST_IMG,
  },
  {
    id: 'floor-level2',
    name: "SECOND FLOOR",
    level: "Second Floor",
    subtitle: "Women's Fashion, Ethnic Pavilion & Western Couture",
    subcategories: [
      "Women's Western Wear & Dresses",
      "Ethnic Pavilion & Bridal Kurtas (Biba, Aurelia, W)",
      "Fusion Wear & Contemporary Tunics",
      "Women's Footwear & Stilettos",
      "Lingerie & Nightwear Studio",
      "Personal Shopper Suite"
    ],
    aisle: "Aisles 17 – 24",
    imageUrl: SECOND_IMG,
  },
  {
    id: 'floor-level3',
    name: "THIRD FLOOR",
    level: "Third Floor",
    subtitle: "Kids' Fashion, Home Decor & Travel Accessories",
    subcategories: [
      "Kids' Wear (Infants, Boys & Girls)",
      "Toys & Creative Play Station",
      "Home & Living (Bedding, Bath & Decor)",
      "Travel Gear & Hard Shell Luggage",
      "Café & Refreshment Lounge"
    ],
    aisle: "Aisles 25 – 32",
    imageUrl: THIRD_IMG,
  },
];

export const TRENDING_EDITS: TrendingEdit[] = [
  {
    id: 'trend-denim',
    title: "The Denim Edit",
    tag: "First & Second Floor Racks",
    imageUrl: HERO_AUTUMN_IMG,
    location: "First Floor Denim Studio",
    description: "High-waisted, wide-leg cutouts and vintage washes trending across both men's and women's aisles.",
  },
  {
    id: 'trend-summer',
    title: "Summer Essentials",
    tag: "Ground & Second Floor",
    imageUrl: WOMEN_IMG,
    location: "Second Floor Western Section",
    description: "Breathable pure linens, floral pastels, and wide brim sun hats curated for warm weather elegance.",
  },
  {
    id: 'trend-beauty',
    title: "Beauty Must-Haves",
    tag: "Ground Floor Atrium",
    imageUrl: BEAUTY_IMG,
    location: "Ground Floor Beauty Bar",
    description: "Dewy skin tints, hyaluronic serums, and signature matte lipsticks on live demo counters today.",
  },
  {
    id: 'trend-workwear',
    title: "Workwear Refresh",
    tag: "First & Second Floor",
    imageUrl: MEN_IMG,
    location: "First Floor Tailoring Section",
    description: "Structured blazers, crease-resistant trousers, and polished footwear for a crisp 9-to-5 look.",
  },
];

export const IN_STORE_EVENTS: InStoreEvent[] = [
  {
    id: 'evt-1',
    title: "Complimentary Beauty Makeover",
    location: "Ground Floor • M.A.C Counter",
    time: "Ongoing Today • 11:00 AM - 8:00 PM",
    badge: "Free Consultation",
    description: "Get a 15-minute quick glam makeover or shade matching by M.A.C master beauty artists.",
  },
  {
    id: 'evt-2',
    title: "Personal Shopper Styling Session",
    location: "Second Floor • VIP Lounge",
    time: "Book at First Citizen Desk",
    badge: "VIP Privilege",
    description: "Curated wardrobe styling tailored to your preferences by Shoppers Stop expert image consultants.",
  },
];
