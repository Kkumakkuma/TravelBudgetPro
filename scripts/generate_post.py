"""
TravelBudgetPro Auto Post Generator
Generates SEO-optimized budget travel articles using OpenAI GPT API
and commits them to the blog repository.
"""

from openai import OpenAI
import datetime
import os
import random
import re

# High CPC keyword categories for budget travel
TOPIC_POOLS = {
    "budget_travel": [
        "How to Travel Europe on $50 a Day in {year}",
        "{number} Ways to Save Money on Your Next Vacation",
        "How to Travel the World on a Tight Budget",
        "Budget Travel Guide: Southeast Asia for Under $30 a Day",
        "How to Plan an Affordable Dream Vacation in {year}",
        "{number} Countries Where Your Dollar Goes the Furthest",
        "How to Travel Full-Time on a Part-Time Budget",
    ],
    "destinations": [
        "Best Budget-Friendly Destinations in Europe for {year}",
        "{number} Cheapest Countries to Visit in {year}",
        "Best Affordable Beach Destinations Around the World",
        "Top {number} Underrated Travel Destinations That Won't Break the Bank",
        "Best Cities for Budget Travelers in South America",
        "Affordable Island Getaways You Need to Visit in {year}",
        "{number} Hidden Gem Destinations for Budget Travelers",
    ],
    "travel_tips": [
        "Best Travel Credit Cards for Saving Money in {year}",
        "How to Find Cheap Flights: {number} Proven Strategies",
        "How to Get Free Hotel Upgrades Every Time",
        "{number} Travel Apps That Save You Hundreds of Dollars",
        "How to Use Travel Rewards Points Like a Pro",
        "Best Time to Book Flights for the Cheapest Fares in {year}",
        "How to Negotiate Better Prices While Traveling Abroad",
    ],
    "packing": [
        "Packing Light: How to Travel with Just a Carry-On",
        "The Ultimate Packing Checklist for Budget Travelers",
        "{number} Packing Mistakes That Cost You Money",
        "Best Travel Gear Under $50 for {year}",
        "How to Pack for a Two-Week Trip in a Backpack",
        "Minimalist Packing Guide: {number} Items You Actually Need",
        "Best Carry-On Backpacks for Budget Travel in {year}",
    ],
    "solo_travel": [
        "Solo Travel Safety Tips: {number} Rules to Follow",
        "Best Destinations for Solo Travelers on a Budget in {year}",
        "How to Meet People While Traveling Solo",
        "Solo Female Travel Safety Guide for {year}",
        "{number} Reasons Why Solo Travel Is Worth It",
        "How to Save Money as a Solo Traveler",
        "Best Hostels for Solo Travelers in Europe",
    ],
    "food_travel": [
        "How to Eat Like a Local on a Budget in Any Country",
        "{number} Street Food Destinations Every Foodie Must Visit",
        "How to Save Money on Food While Traveling",
        "Best Food Markets Around the World for Budget Travelers",
        "How to Cook While Traveling: {number} Easy Hostel Recipes",
        "Cheapest Countries for Amazing Food in {year}",
        "Street Food Safety Tips: How to Eat Safely Abroad",
    ],
    "travel_hacks": [
        "{number} Travel Hacks That Save You Serious Money",
        "How to Find Mistake Fares and Error Prices on Flights",
        "Best Budget Airlines Around the World in {year}",
        "How to Get Airport Lounge Access for Free",
        "Travel Hack: How to Fly Business Class on a Budget",
        "{number} Secret Websites for Finding Cheap Travel Deals",
        "How to Use VPNs to Find Cheaper Flights and Hotels",
    ],
}

SYSTEM_PROMPT = """You are an expert travel writer for a blog called TravelBudgetPro.
Write SEO-optimized, informative, and engaging blog posts about budget travel, destinations, and money-saving travel strategies.

Rules:
- Write in a friendly, adventurous but practical tone
- Use short paragraphs (2-3 sentences max)
- Include practical, actionable tips with specific dollar amounts where possible
- Use headers (##) to break up sections
- Include bullet points and numbered lists where appropriate
- Write between 1200-1800 words
- Naturally include the main keyword 3-5 times
- Include a compelling introduction that hooks the reader
- End with a clear conclusion/call-to-action
- Do NOT include any AI disclaimers or mentions of being AI-generated
- Write as if you are a seasoned budget traveler sharing personal experience and expertise
- Include specific costs, hostel/hotel price ranges, and daily budget breakdowns
- Mention specific tools, apps, and websites travelers can use
- Include safety tips where appropriate
- Do NOT use markdown title (# Title) - just start with the content
"""


def pick_topic():
    """Select a random topic from the pools."""
    year = datetime.datetime.now().year
    number = random.choice([3, 5, 7, 10, 12, 15])
    category = random.choice(list(TOPIC_POOLS.keys()))
    title_template = random.choice(TOPIC_POOLS[category])
    title = title_template.format(year=year, number=number)
    return title, category


def generate_post_content(title, category):
    """Generate a blog post using OpenAI GPT API."""
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Write a comprehensive blog post with the title: \"{title}\"\n\nCategory: {category.replace('_', ' ')}\n\nRemember to write 1200-1800 words, use ## for section headers, and make it SEO-friendly with practical budget travel advice.",
            },
        ],
    )

    return response.choices[0].message.content


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_repo_root():
    """Get the repository root directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_existing_titles():
    """Get titles of existing posts to avoid duplicates."""
    posts_dir = os.path.join(get_repo_root(), '_posts')
    titles = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                title_part = filename[11:-3]
                titles.add(title_part)
    return titles


def create_post():
    """Generate and save a new blog post."""
    existing = get_existing_titles()

    # Try up to 10 times to find a non-duplicate topic
    for _ in range(10):
        title, category = pick_topic()
        slug = slugify(title)
        if slug not in existing:
            break
    else:
        title, category = pick_topic()
        slug = slugify(title) + f"-{random.randint(100, 999)}"

    print(f"Generating post: {title}")
    print(f"Category: {category}")

    content = generate_post_content(title, category)

    # Create the post file
    today = datetime.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}-{slug}.md"

    posts_dir = os.path.join(get_repo_root(), '_posts')
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)

    # Create frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category.replace('_', '-')}]
description: "{title} - Practical budget travel tips and guides for every adventurer."
---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"Post saved: {filepath}")
    return filepath, filename

if __name__ == '__main__':
    # Every 5th post: generate a Gumroad promo post
    from promo_post import should_write_promo, create_promo_post
    if should_write_promo():
        print("Generating promotional post...")
        filepath, filename = create_promo_post()
    else:
        filepath, filename = create_post()
    print(f"Done! Post generated: {filename}")
