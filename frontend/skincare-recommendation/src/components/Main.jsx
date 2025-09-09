import { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStar as solidStar, faStarHalfAlt } from '@fortawesome/free-solid-svg-icons';
import { faStar as regularStar } from '@fortawesome/free-regular-svg-icons';

function MainPage() {
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({
    brand: "",
    category: "",
    skin_type: "",
    concern: "",
    min_price: "",
    max_price: "",
    sort_by: "",
  });
  const [products, setProducts] = useState([]);
  const [brands, setBrands] = useState(["Brand1", "Brand2"]); // جایگزین با API
  const [categories, setCategories] = useState(["Category1", "Category2"]); // جایگزین با API
  const [skinTypes, setSkinTypes] = useState(["Dry", "Oily", "Normal"]); // جایگزین با API
  const [showFilter, setShowFilter] = useState(false);
  const [showFilterّForm, setShowFilterForm] = useState(false);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    let url = "http://127.0.0.1:8000/api/mainpage/";
    if (searchQuery) {
      url += `?q=${encodeURIComponent(searchQuery)}`;
    }
    fetch(url)
      .then((res) => res.json())
      .then((data) => setProducts(data))
      .catch((err) => console.error(err));
  }, [searchQuery]);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const toggleFilter = () => {
    if (windowWidth < 576) {
      setShowFilter((prev) => !prev);
      setShowFilterForm((prev) => !prev);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleSearchInputChange = (e) => {
    setSearchInput(e.target.value);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setSearchQuery(searchInput);
  };

  const formatter = new Intl.NumberFormat('fa-IR');

  function StarRating({ rating }) {
    const fullStars = Math.floor(rating);
    const halfStar = rating - fullStars >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
  
    return (
      <p className="rate" style={{ display: "flex", gap: "0px" }}>
        {Array(fullStars).fill(0).map((_, i) => (
          <FontAwesomeIcon key={"f"+i} icon={solidStar} className="star-gold" color="gold" size="sm" />
        ))}
        {halfStar && <FontAwesomeIcon icon={faStarHalfAlt} className="star-gold" color="gold" size="sm" />}
        {Array(emptyStars).fill(0).map((_, i) => (
          <FontAwesomeIcon key={"e"+i} icon={regularStar} className="star-gold" color="gold" size="sm" />
        ))}
      </p>
    );
  }



  return (
      <div className="container" id="container">
        {/* بخش جستجو */}
        <section className="search-bar">
          <form className="search-form" onSubmit={handleSearchSubmit}>
            <div id="search_js" className="search_box">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="1.5"
                stroke="currentColor"
                className="size-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
                />
              </svg>
              <input
                type="text"
                name="q"
                id="search-input"
                placeholder="جستجو"
                autoComplete="off"
                value={searchInput}
                onChange={handleSearchInputChange}
              />
            </div>
            <button className="page_button" type="submit">
              جستجو
            </button>
          </form>
          <div id="suggestions" className="suggestions-box"></div>
        </section>

        {/* بخش محصولات و فیلتر */}
        <section className="products-box">
          <aside 
            id="aside"
            style={{
              border: windowWidth < 576 && showFilter ? "1px solid #ccc" : "none",
              padding: windowWidth < 576 && showFilter ? "10px 5px 10px" : "0px 0 0",
            }}
            >
            <h3 className="filter-title" id="filter-toggle" onClick={toggleFilter}>
              فیلتر محصولات
              <svg
                version="1.1"
                className="has-solid"
                viewBox="0 0 36 36"
                preserveAspectRatio="xMidYMid meet"
                xmlns="http://www.w3.org/2000/svg"
                focusable="false"
                role="img"
                width="28"
                height="28"
                fill="currentColor"
              >
                <path
                  className="clr-i-outline clr-i-outline-path-1"
                  d="M33,4H3A1,1,0,0,0,2,5V6.67a1.79,1.79,0,0,0,.53,1.27L14,19.58v10.2l2,.76V19a1,1,0,0,0-.29-.71L4,6.59V6H32v.61L20.33,18.29A1,1,0,0,0,20,19l0,13.21L22,33V19.5L33.47,8A1.81,1.81,0,0,0,34,6.7V5A1,1,0,0,0,33,4Z"
                />
              </svg>
            </h3>

            <form className="filter-form" id="filter-menu"
                style={{
                    display: windowWidth < 576 && showFilterّForm ? "flex" : "none"
                }}
            >
              {/* برند */}
              <div className="filter-group">
                <label>برند:</label>
                <select name="brand" value={filters.brand} onChange={handleFilterChange}>
                  <option value="">همه</option>
                  {brands.map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>

              {/* دسته بندی */}
              <div className="filter-group">
                <label>دسته‌بندی:</label>
                <select name="category" value={filters.category} onChange={handleFilterChange}>
                  <option value="">همه</option>
                  {categories.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              {/* نوع پوست */}
              <div className="filter-group">
                <label>نوع پوست:</label>
                <select name="skin_type" value={filters.skin_type} onChange={handleFilterChange}>
                  <option value="">همه</option>
                  {skinTypes.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              {/* مشکل پوستی */}
              <div className="filter-group">
                <label>مشکل پوستی:</label>
                <input
                  type="text"
                  name="concern"
                  value={filters.concern}
                  placeholder="مثلا جوش"
                  onChange={handleFilterChange}
                />
              </div>

              {/* قیمت */}
              <div className="filter-group price-group">
                <label>قیمت:</label>
                <input
                  type="number"
                  name="min_price"
                  value={filters.min_price}
                  placeholder="حداقل"
                  onChange={handleFilterChange}
                />
                <input
                  type="number"
                  name="max_price"
                  value={filters.max_price}
                  placeholder="حداکثر"
                  onChange={handleFilterChange}
                />
              </div>

              {/* مرتب‌سازی */}
              <div className="filter-group">
                <label>مرتب‌سازی:</label>
                <select name="sort_by" value={filters.sort_by} onChange={handleFilterChange}>
                  <option value="">پیش‌فرض</option>
                  <option value="price_low">قیمت کم به زیاد</option>
                  <option value="price_high">قیمت زیاد به کم</option>
                  <option value="rating">بالاترین امتیاز</option>
                  <option value="popularity">محبوبیت</option>
                </select>
              </div>

              <button type="submit" className="page_button">اعمال فیلتر</button>
            </form>
          </aside>

          {/* نمایش محصولات */}
          <div className="products">
            {products.length === 0 ? (
              <p>محصولی برای نمایش وجود ندارد.</p>
            ) : (
              products.map((product) => (
                <a key={product.id} href={`/product/${product.id}`} className="product_card">
                  <div className="product_image_div">
                    <img src={product.image} alt={product.name} className="product_image" />
                  </div>
                  <div className="product_info">
                    <p className="product_name">{product.name}</p>
                    <p className="product_brand">برند {product.brand}</p>
                    <p className="product_price">{formatter.format(product.price)} تومان</p>
                    <div className="product_view-and-rate">
                        <p className="view">{formatter.format(product.views)} بازدید</p>
                        <StarRating rating={product.rating} />
                    </div>
                  </div>
                </a>
              ))
            )}
          </div>
        </section>
      </div>
  );
}

export default MainPage;
