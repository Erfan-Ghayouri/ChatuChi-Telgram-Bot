"""
Pagination utilities for inline keyboards.
"""

from typing import Any


def paginate_list(
    items: list[Any],
    page: int = 0,
    per_page: int = 10,
) -> tuple[list[Any], int, int]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Current page number (0-indexed)
        per_page: Items per page
        
    Returns:
        Tuple of (page_items, total_pages, current_page)
    """
    total_items = len(items)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    
    # Ensure page is within bounds
    page = max(0, min(page, total_pages - 1))
    
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, total_items)
    
    page_items = items[start_idx:end_idx]
    
    return page_items, total_pages, page


def create_pagination_buttons(
    current_page: int,
    total_pages: int,
    callback_prefix: str = "page",
) -> list[list[dict[str, Any]]]:
    """
    Create pagination button rows for inline keyboard.
    
    Args:
        current_page: Current page number (0-indexed)
        total_pages: Total number of pages
        callback_prefix: Prefix for callback data
        
    Returns:
        List of button rows
    """
    if total_pages <= 1:
        return []
    
    buttons = []
    
    # Navigation row
    nav_row = []
    
    # Previous button
    if current_page > 0:
        nav_row.append({
            "text": "◀️ Prev",
            "callback_data": f"{callback_prefix}_{current_page - 1}",
        })
    
    # Page numbers (show up to 5 pages)
    pages_to_show = get_visible_pages(current_page, total_pages, max_visible=5)
    for page_num in pages_to_show:
        if page_num == current_page:
            nav_row.append({
                "text": f"● {page_num + 1} ●",
                "callback_data": f"{callback_prefix}_{page_num}",
            })
        else:
            nav_row.append({
                "text": str(page_num + 1),
                "callback_data": f"{callback_prefix}_{page_num}",
            })
    
    # Next button
    if current_page < total_pages - 1:
        nav_row.append({
            "text": "Next ▶️",
            "callback_data": f"{callback_prefix}_{current_page + 1}",
        })
    
    if nav_row:
        buttons.append(nav_row)
    
    return buttons


def get_visible_pages(
    current_page: int,
    total_pages: int,
    max_visible: int = 5,
) -> list[int]:
    """
    Get list of page numbers to display.
    
    Shows current page centered with surrounding pages.
    """
    if total_pages <= max_visible:
        return list(range(total_pages))
    
    half = max_visible // 2
    start = max(0, current_page - half)
    end = min(total_pages, start + max_visible)
    
    # Adjust if we're near the end
    if end - start < max_visible:
        start = max(0, end - max_visible)
    
    return list(range(start, end))
