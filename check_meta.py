import instaloader
L = instaloader.Instaloader()
post = instaloader.Post.from_shortcode(L.context, "DZhnD1wjEgd")
print("IS VIDEO:", post.is_video)
print("URL:", post.url)
print("VIDEO URL:", post.video_url)
