import { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStar as solidStar, faStarHalfAlt } from '@fortawesome/free-solid-svg-icons';
import { faStar as regularStar } from '@fortawesome/free-regular-svg-icons';
import './../styles/defaults/product-card.css';
import "../styles/defaults/button.css"
import "../assets/fonts/font.css"
import { useAuth } from "../authContext"

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
  const [brands, setBrands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [skinTypes, setSkinTypes] = useState([]);
  const [showFilter, setShowFilter] = useState(false);
  const [showFilterForm, setShowFilterForm] = useState(false);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  const [activeFilters, setActiveFilters] = useState(filters);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const { user, token } = useAuth();

  useEffect(() => {
    const root = document.getElementById("root");
    root.classList.add("page-main");
    return () => {
      root.classList.remove("page-main");
    };
  }, []);

  useEffect(() => {
  const fetchMainpage = async () => {
    try {
      setLoading(true);

      const params = new URLSearchParams();
      params.append("page", page);
      params.append("page_size", 40);

      if (searchQuery) params.append("q", searchQuery);
      if (activeFilters.brand) params.append("brand", activeFilters.brand);
      if (activeFilters.category) params.append("category", activeFilters.category);
      if (activeFilters.skin_type) params.append("skin_type", activeFilters.skin_type);
      if (activeFilters.min_price) params.append("min_price", activeFilters.min_price);
      if (activeFilters.max_price) params.append("max_price", activeFilters.max_price);
      if (activeFilters.sort_by) params.append("sort_by", activeFilters.sort_by);
      // if (user) params.append("user_id", user.id);

      const host = window.location.hostname;

      const headers = {};
      if (token?.access) {
        headers["Authorization"] = `Bearer ${token.access}`;
      }

      const url = `http://${host}:8000/api/mainpage/?${params.toString()}`;

      const res = await fetch(url, { headers });
      if (!res.ok) throw new Error("خطا در دریافت لیست محصولات");

      const data = await res.json();

      setProducts(data.results.products);
      setBrands(data.results.brands);
      setCategories(data.results.categories);
      setSkinTypes(data.results.skin_types);
      setTotalPages(Math.ceil(data.count / 40));

    } catch (err) {
      console.error("❌ خطا در fetchMainpage:", err);
    } finally {
      setLoading(false);
    }
  };

  fetchMainpage();
}, [searchQuery, activeFilters, user, page, token]);



  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const widthForForm = 1000
  const toggleFilter = () => {
    if (windowWidth < widthForForm) {
      setShowFilter((prev) => !prev);
      setShowFilterForm((prev) => !prev);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleApplyFilters = (e) => {
    e.preventDefault();
    setActiveFilters(filters);
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
                className="main-search-input"
                type="text"
                name="q"
                id="search-input"
                placeholder="جستجو"
                autoComplete="off"
                value={searchInput}
                onChange={handleSearchInputChange}
              />
            </div>
            <button className="page_button search-form-button" type="submit">
              جستجو
            </button>
          </form>
          <div id="suggestions" className="suggestions-box"></div>
        </section>

        {/* بخش محصولات و فیلتر */}
        <section className="products-and-filter">
          <aside 
            id="aside"
            style={{
              border: windowWidth < widthForForm && showFilter ? "1px solid #ccc" : "none",
              padding: windowWidth < widthForForm && showFilter ? "10px 5px 10px" : "0px 0 0",
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
                    display: windowWidth < widthForForm ? (showFilterForm ? "flex" : "none") : "flex",
                }}
                onSubmit={handleApplyFilters}
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
          
          <div className="products-box">
          {/* نمایش محصولات */}
            <div className="recommendations-grid">
              {products.length === 0 ? (
                <p>بارگذاری محصولات ...</p>
              ) : (
                products.map((product) => (
                  <a
                    key={product.id}
                    href={`/product/${product.id}/`}
                    className="recommendation-card"
                  >
                    <div className="card-header">
                      <img
                        src={product.image}
                        alt={product.name}
                        className="product-image"
                      />
                      <div className="product-info">
                        <div className="product-name">{product.name}</div>
                        <div className="product-brand">{product.brand}</div>
                        <div className="product-price">
                          <svg style={{ width: '20px', fill: 'white'}} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="size-6">
                            <path fillRule="evenodd" d="M5.25 2.25a3 3 0 0 0-3 3v4.318a3 3 0 0 0 .879 2.121l9.58 9.581c.92.92 2.39 1.186 3.548.428a18.849 18.849 0 0 0 5.441-5.44c.758-1.16.492-2.629-.428-3.548l-9.58-9.581a3 3 0 0 0-2.122-.879H5.25ZM6.375 7.5a1.125 1.125 0 1 0 0-2.25 1.125 1.125 0 0 0 0 2.25Z" clipRule="evenodd" />
                          </svg>
                          {formatter.format(product.price)} تومان
                        </div>
                      </div>
                    </div>
                    <div className="reason">
                      <i className="fas fa-lightbulb" style={{ color: "rgb(184, 178, 101)" }}></i>
                        {product.reason}
                    </div>
                        <div className="view-rate">
                            <div className="view">
                              <i className="fas fa-eye" style={{ color: "rgb(145, 135, 235)" }}></i>
                              {formatter.format(product.views)} بازدید
                            </div>
                            <div className="rate">
                              ⭐ {formatter.format(product.rating)}/{formatter.format(5)}
                            </div>
                        </div>
                    </a>
                  ))
              )}
            </div>
            <div className="pagination">
              <button className="pagination-button" disabled={page === 1} onClick={() => setPage(page - 1)}>قبلی</button>
              <span>{formatter.format(page)} از {formatter.format(totalPages)}</span>
              <button className="pagination-button" disabled={page === totalPages} onClick={() => setPage(page + 1)}>بعدی</button>
            </div>
          </div>
        </section>
      </div>
  );
}

export default MainPage;
