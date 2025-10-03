import csv
import os
from datetime import datetime

PRODUCTS_FILE = 'products.csv'
SALES_FILE = 'sales.csv'
LOW_STOCK_THRESHOLD = 5

def load_products():
    products = {}
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products[row['id']] = {
                    'name': row['name'],
                    'price': float(row['price']),
                    'stock': int(row['stock'])
                }
    return products

def save_products(products):
    with open(PRODUCTS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'price', 'stock'])
        writer.writeheader()
        for pid, info in products.items():
            writer.writerow({
                'id': pid,
                'name': info['name'],
                'price': info['price'],
                'stock': info['stock']
            })

def add_product(products):
    pid = input("Product ID: ")
    if pid in products:
        print("Product ID already exists.")
        return
    name = input("Name: ")
    price = float(input("Price: "))
    stock = int(input("Stock Quantity: "))
    products[pid] = {'name': name, 'price': price, 'stock': stock}
    print("Product added.")

def update_product(products):
    pid = input("Product ID to update: ")
    if pid not in products:
        print("Product not found.")
        return
    print("Leave field empty to keep current value.")
    name = input(f"New Name ({products[pid]['name']}): ") or products[pid]['name']
    price_in = input(f"New Price ({products[pid]['price']}): ")
    price = float(price_in) if price_in else products[pid]['price']
    stock_in = input(f"New Stock ({products[pid]['stock']}): ")
    stock = int(stock_in) if stock_in else products[pid]['stock']
    products[pid] = {'name': name, 'price': price, 'stock': stock}
    print("Product updated.")

def delete_product(products):
    pid = input("Product ID to delete: ")
    if pid in products:
        del products[pid]
        print("Product deleted.")
    else:
        print("Product not found.")

def search_product(products):
    query = input("Enter product name or ID: ").lower()
    for pid, info in products.items():
        if pid.lower() == query or info['name'].lower() == query:
            print(f"ID: {pid}, Name: {info['name']}, Price: {info['price']}, Stock: {info['stock']}")
            return
    print("Product not found.")

def add_to_cart(products, cart):
    pid = input("Product ID to add: ")
    if pid not in products:
        print("Product not found.")
        return
    qty = int(input("Quantity: "))
    if qty > products[pid]['stock']:
        print("Insufficient stock.")
        return
    if pid in cart:
        cart[pid]['qty'] += qty
    else:
        cart[pid] = {'name': products[pid]['name'], 'price': products[pid]['price'], 'qty': qty}
    print(f"Added {qty} of {products[pid]['name']} to cart.")

def process_order(products):
    cart = {}
    while True:
        add_to_cart(products, cart)
        cont = input("Add more items? (y/n): ")
        if cont.lower() != 'y':
            break
    total = sum(v['price'] * v['qty'] for v in cart.values())
    discount = 0
    apply_discount = input("Apply discount? (y/n): ")
    if apply_discount.lower() == 'y':
        discount = float(input("Discount amount: "))
    bill_total = total - discount
    print("\n--- BILL ---")
    print(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for pid, info in cart.items():
        print(f"{info['name']}: {info['qty']} x {info['price']} = {info['qty']*info['price']}")
    print(f"Subtotal: {total}")
    print(f"Discount: {discount}")
    print(f"Total: {bill_total}")
    save_choice = input("Save bill? (y/n): ")
    if save_choice.lower() == 'y':
        save_bill(cart, bill_total)
    for pid in cart:
        products[pid]['stock'] -= cart[pid]['qty']
    record_sale(cart, bill_total)
    print("Order processed.")

def save_bill(cart, total):
    fname = input("Save as filename (bill.txt/csv): ")
    ext = filename_extension(fname)
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if ext == ".txt":
        with open(fname, 'w') as f:
            f.write("--- BILL ---\n")
            f.write(f"Date/Time: {now_str}\n")
            for pid, info in cart.items():
                f.write(f"{info['name']}: {info['qty']} x {info['price']} = {info['qty']*info['price']}\n")
            f.write(f"Total: {total}\n")
    elif ext == ".csv":
        with open(fname, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date/Time', now_str,'',''])
            writer.writerow(['Product', 'Qty', 'Price', 'Subtotal'])
            for pid, info in cart.items():
                writer.writerow([info['name'], info['qty'], info['price'], info['qty']*info['price']])
            writer.writerow(['Total', '', '', total])
    print("Bill saved.")

def filename_extension(fname):
    _, ext = os.path.splitext(fname)
    return ext

def record_sale(cart, total):
    now = datetime.now()
    rows = []
    for pid, info in cart.items():
        rows.append([
            now.strftime('%Y-%m-%d %H:%M:%S'), # Include time for better tracking
            pid,
            info['name'],
            info['qty'],
            info['price'],
            info['qty'] * info['price'],
            '' # Add an empty column to match the total row structure
        ])
    # Ensure the sales file has a header if it's being created
    file_exists = os.path.exists(SALES_FILE)
    with open(SALES_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
             writer.writerow(['Date/Time', 'Product ID', 'Product Name', 'Quantity', 'Price', 'Subtotal', 'Order Total'])
        for row in rows:
            writer.writerow(row)
        # Write the total row with consistent columns
        writer.writerow([now.strftime('%Y-%m-%d %H:%M:%S'), 'ORDER_TOTAL', '', '', '', '', total])


def daily_sales_report():
    date_str = input("Enter date (YYYY-MM-DD): ")
    total = 0
    if os.path.exists(SALES_FILE):
        with open(SALES_FILE, newline='') as f:
            reader = csv.reader(f)
            header = next(reader) # Read header row
            try:
                # Find the index of the 'Order Total' column
                order_total_col_index = header.index('Order Total')
            except ValueError:
                print("Error: 'Order Total' column not found in sales file.")
                return

            for row in reader:
                try:
                    # Ensure the row has enough columns before accessing by index
                    if len(row) > order_total_col_index:
                        sale_date_str = row[0]
                        item_id = row[1]

                        sale_date = datetime.strptime(sale_date_str.split()[0], '%Y-%m-%d').date() # Extract date and parse
                        if sale_date.strftime('%Y-%m-%d') == date_str and item_id == 'ORDER_TOTAL':
                            total += float(row[order_total_col_index])
                except (ValueError, IndexError) as e:
                    # Handle potential errors in row format or parsing
                    print(f"Skipping invalid row: {row} - Error: {e}")
                    pass
    print(f"Total sales for {date_str}: {total}")

def report_low_stock(products):
    print("Low Stock Products:")
    for pid, info in products.items():
        if info['stock'] < LOW_STOCK_THRESHOLD:
            print(f"ID: {pid}, {info['name']} - Stock: {info['stock']}")

def menu():
    products = load_products()
    while True:
        print("\nInventory & Billing Menu")
        print("1. Add Product")
        print("2. Update Product")
        print("3. Delete Product")
        print("4. Search Product")
        print("5. Process Order")
        print("6. Daily Sales Report")
        print("7. Low Stock Report")
        print("8. Save & Quit")
        choice = input("Select option: ")
        if choice == '1':
            add_product(products)
        elif choice == '2':
            update_product(products)
        elif choice == '3':
            delete_product(products)
        elif choice == '4':
            search_product(products)
        elif choice == '5':
            process_order(products)
        elif choice == '6':
            daily_sales_report()
        elif choice == '7':
            report_low_stock(products)
        elif choice == '8':
            save_products(products)
            print("Changes saved. Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__== "__main__":
    menu()
