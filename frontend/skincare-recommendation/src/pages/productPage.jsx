import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../authUser";
import "../styles/product_page/style.css"

// Utility functions
const toPersianDigits = (str) => str.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
const addComma = (n) => n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

const ProductPage = () => {
    const { id } = useParams();
    const { user } = useAuth();

    const [product, setProduct] = useState(null);
    const [comments, setComments] = useState([]);
    const [liked, setLiked] = useState(false);
    const [commentedBefore, setCommentedBefore] = useState(false);

    const [currentRating, setCurrentRating] = useState(3);
    const [likeActive, setLikeActive] = useState(false);
    const [likeCount, setLikeCount] = useState(0);
    const [cartCount, setCartCount] = useState(0);
    const [commentText, setCommentText] = useState("");
    const [error, setError] = useState(false);

    const userMenuRef = useRef(null);

    useEffect(() => {
        const root = document.getElementById("root");
        root.classList.add("product-page-root");
        return () => {
          root.classList.remove("product-page-root");
        };
    }, []);

    useEffect(() => {
        const fetchData = async () => {
            try {
                let url = `http://127.0.0.1:8000/api/products/${id}/`;
                if (user && user.id) {
                    url += `?user_id=${user.id}`;
                }

                const res = await fetch(url);
                if (!res.ok) throw new Error("خطا در دریافت محصول");
                const data = await res.json();

                setProduct(data.product);
                setComments(data.comments || []);
                setLiked(data.liked || false);
                setCommentedBefore(data.commented_before || false);
                setLikeCount(data.product.likes);
                setCartCount(data.product.cart_count || 0);
            } catch (err) {
                console.error(err);
            }
        };

        fetchData();
    }, [id, user]);

    if (!product) return <p>در حال بارگذاری محصول...</p>;

    // Handle Like
    const handleLike = async () => {
        if (!user) return;
        try {
            const res = await fetch(`/like/${product.id}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    product_id: product.id,
                    user_id: user.id,
                }),
            });
            if (!res.ok) throw new Error("خطا در ارسال لایک");
            const data = await res.json();
            setLikeCount(data.likes);
            setLikeActive(!likeActive);
        } catch (err) {
            console.error(err);
        }
    };

    // Handle Add to Cart
    const handleAddToCart = async (e) => {
        e.preventDefault();
        if (!user) return;
        try {
            const res = await fetch(`/profiles/add-to-cart/${product.id}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({}),
            });
            const data = await res.json();
            if (res.ok) {
                setCartCount(data.cart_count);
                alert("محصول به سبد خرید اضافه شد!");
            } else {
                alert("خطا در افزودن به سبد خرید");
            }
        } catch {
            alert("خطا در افزودن به سبد خرید");
        }
    };

    // Handle Comment Form Submit
    const handleCommentSubmit = async (e) => {
        e.preventDefault();
        if (!commentText.trim()) {
            setError(true);
            return;
        }
        setError(false);
      
        try {
            const res = await fetch(`/api/comments/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    product_id: product.id,
                    user_id: user.id,
                    text: commentText,
                    rating: currentRating,
                }),
            });
            const data = await res.json();
            if (res.ok) {
                setComments((prev) => [...prev, data]); // کامنت جدید رو اضافه کن
                setCommentText("");
            } else {
                alert("خطا در ثبت نظر");
            }
        } catch (err) {
            console.error(err);
        }
    };


    return (
        <div className="product-page">

            <main id="container" className="container">
                <section className="product_info">
                    <div className="main_info">
                        <img src={product.image} className="product_image" alt={product.name} />
                        <div className="image_underline"></div>
                        <div className="product_details">
                            <div className="interactions-mobile">
                                <span className="product_rating">
                                    <span className="star">&#9733;</span>
                                    <span style={{ marginRight: -5 }}>
                                        <span className="hide_text">امتیاز</span> {toPersianDigits(product.rating)}
                                        <span className="hide_text">
                                            براساس نظر {toPersianDigits(addComma(product.sales_count))} خریدار
                                        </span>
                                    </span>
                                    <span style={{ opacity: 0.4 }}>|</span>
                                    <span>{toPersianDigits(addComma(product.views))} بازدید</span>
                                    <span style={{ opacity: 0.4 }}>|</span>
                                    <svg
                                        className="heart-ico size-6"
                                        xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 24 24"
                                        fill="currentColor"
                                        onClick={handleLike}
                                    >
                                        <path d="M11.645 20.91-.007-.003-.022-.012a15.247 15.247 0 0 1-.383-.218 25.18 25.18 0 0 1-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0 1 12 5.052 5.5 5.5 0 0 1 16.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 0 1-4.244 3.17.752.752 0 0 1-.704 0Z" />
                                    </svg>
                                    <span id="like-count">{toPersianDigits(addComma(likeCount))}</span>
                                </span>
                            </div>

                            <h3>مشخصات محصول {toPersianDigits(product.count)}</h3>
                            <p className="product_name">نام: {product.name}</p>
                            <p className="product_brand">برند: {product.brand}</p>
                            <p className="product_price">
                                قیمت: {toPersianDigits(addComma(product.price))} تومان
                            </p>
                        </div>
                    </div>

                    <div className="product_add_exp">
                        <div className="product_introduction">
                            <h3>معرفی محصول</h3>
                            <p>{product.description}</p>
                        </div>
                        <div className="ingredients">
                            <h3>مواد تشکیل دهنده</h3>
                            <p>{product.ingredients.join("، ")}</p>
                        </div>
                        <div className="category">
                            <h3>دسته بندی</h3>
                            <p>{product.category}</p>
                        </div>
                        <div className="concerns_targeted">
                            <h3>موارد استفاده</h3>
                            <p>{product.concerns_targeted.join("، ")}</p>
                        </div>
                        <div className="product_suitable">
                            <h3>مناسب برای</h3>
                            <p>پوست های {product.skin_types.join("، ")}</p>
                        </div>
                        <div className="product_usage">
                            <h3>نحوه ی استفاده</h3>
                            <p>{product.usage}</p>
                        </div>
                    </div>

                    <div className="add_product_to_cart">
                        {user ? (
                            <form className="add-to-cart-form" onSubmit={handleAddToCart}>
                                <button type="submit" className="page_button">
                                    افزودن به سبد خرید
                                </button>
                            </form>
                        ) : (
                            <p>
                                برای افزودن به سبد خرید وارد حساب{" "}
                                <a href={`/login?next=${window.location.pathname}`}>حساب کاربری</a> شوید
                            </p>
                        )}
                    </div>
                </section>

                <section className="users_comments">
                    <h2>نظرات کاربران:</h2>
                    {comments.length > 0 ? (
                        comments.map((comment, i) => (
                            <div className="user_review_box" key={i}>
                                <strong>{comment.user.username}</strong>
                                <span>
                                    (امتیاز کاربر: {toPersianDigits(comment.rating)} از {toPersianDigits(5)})
                                </span>
                                <p className="user_review_text">{comment.text}</p>
                            </div>
                        ))
                    ) : (
                        <p>هنوز نظری برای این محصول ثبت نشده است</p>
                    )}

                    {user && !commentedBefore && (
                        <form onSubmit={handleCommentSubmit}>
                            <label>نظر خود را بنویسید:</label>
                            <textarea
                                value={commentText}
                                onChange={(e) => setCommentText(e.target.value)}
                                required
                            />
                            <label>امتیاز شما:</label>
                            <input
                                type="number"
                                min={1}
                                max={5}
                                value={currentRating}
                                onChange={(e) => setCurrentRating(Number(e.target.value))}
                            />
                            {error && <p style={{ color: "red" }}>متن نظر نمی‌تواند خالی باشد!</p>}
                            <button type="submit">ثبت نظر</button>
                        </form>
                    )}
                </section>
            </main>
        </div>
    );
};

export default ProductPage;
