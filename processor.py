import sqlite3
 
class ShipmentProcessor:
    def __init__(self, db_path):
        self.db_path = db_path
 
    def process_shipment(self, item_name, quantity, log_callback):
        """
        Executes the shipment logic.
        :param item_name: Name of the item
        :param quantity: Amount to move
        :param log_callback: A function to print to the GUI console
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
 
        log_callback(f"--- STARTING TRANSACTION: Move {quantity} of {item_name} ---")
 
        try:
            # (opcjonalnie, ale czytelnie) start transakcji
            cursor.execute("BEGIN")
 
            # STEP 1: Update Inventory
            # Jeśli w bazie jest constraint, który blokuje zejście poniżej 0,
            # to tu poleci sqlite3.IntegrityError
            cursor.execute(
                "UPDATE inventory SET stock_qty = stock_qty - ? WHERE item_name = ?",
                (quantity, item_name)
            )
            log_callback(">> STEP 1 SUCCESS: Inventory Deducted.")
 
            # STEP 2: Log the Shipment (dopiero jeśli step 1 się udał)
            cursor.execute(
                "INSERT INTO shipment_log (item_name, qty_moved) VALUES (?, ?)",
                (item_name, quantity)
            )
            log_callback(">> STEP 2 SUCCESS: Shipment Logged.")
 
            # COMMIT tylko gdy oba kroki się udały
            conn.commit()
            log_callback("--- TRANSACTION COMMITTED ---")
 
        except sqlite3.IntegrityError as e:
            # STEP 1 wywalił się -> COFAMY WSZYSTKO i NIE MA LOGA
            conn.rollback()
            log_callback(f">> TRANSACTION FAILED (STEP 1): {e}")
            log_callback("--- TRANSACTION ROLLED BACK ---")
 
        except Exception as e:
            # jakikolwiek inny błąd (np. przy logowaniu) -> rollback też
            conn.rollback()
            log_callback(f">> TRANSACTION FAILED: {e}")
            log_callback("--- TRANSACTION ROLLED BACK ---")
 
        finally:
            conn.close()