from database.crud_operations import articulo_crud, historial_crud

def test_articulo_get_all():
    """Probar obtener todos los artículos"""
    print("\n🧪 TEST: articulo_crud.get_all()")
    try:
        all_articulos = articulo_crud.get_all()
        print(f"   📊 Total de artículos: {len(all_articulos)}")
        
        if all_articulos:
            print("   📋 Primeros 3 artículos:")
            for i, art in enumerate(all_articulos[:3]):
                print(f"      {i+1}. ID: {art.id}, RTR_ID: {art.rtr_id}, Nombre: {art.nombre}")
        else:
            print("   ℹ️  No hay artículos en la base de datos")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_articulo_insert_one():
    """Probar insertar un artículo"""
    print("\n🧪 TEST: articulo_crud.insert_one()")
    
    product_data = {
        'rtr_id': 99999,
        'nombre': 'Producto Test Individual',
        'precio': 149.99,
        'categoria': 'Electrónicos Test',
        'descripcion': 'Producto para prueba individual'
    }
    
    try:
        result = articulo_crud.insert_one(product_data)
        print(f"   ✅ Artículo insertado: {result}")
        
        # Verificar que se insertó
        exists = articulo_crud.exists_by_rtr_id(99999)
        print(f"   ✅ Verificación de existencia: {exists}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_articulo_bulk_insert():
    """Probar inserción masiva de artículos"""
    print("\n🧪 TEST: articulo_crud.bulk_insert()")
    
    products_list = [
        {
            'rtr_id': 88881,
            'nombre': 'Producto Bulk 1',
            'precio': 50.00,
            'categoria': 'Test Bulk',
            'descripcion': 'Producto bulk 1'
        },
        {
            'rtr_id': 88882,
            'nombre': 'Producto Bulk 2',
            'precio': 75.00,
            'categoria': 'Test Bulk',
            'descripcion': 'Producto bulk 2'
        },
        {
            'rtr_id': 88883,
            'nombre': 'Producto Bulk 3',
            'precio': 100.00,
            'categoria': 'Test Bulk',
            'descripcion': 'Producto bulk 3'
        }
    ]
    
    try:
        result = articulo_crud.bulk_insert(products_list)
        print(f"   ✅ Artículos insertados: {result}")
        
        # Verificar que se insertaron
        for product in products_list:
            exists = articulo_crud.exists_by_rtr_id(product['rtr_id'])
            print(f"   ✅ RTR_ID {product['rtr_id']} existe: {exists}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_articulo_exists_by_rtr_id():
    """Probar verificación de existencia por RTR ID"""
    print("\n🧪 TEST: articulo_crud.exists_by_rtr_id()")
    
    try:
        # Probar con un ID que debería existir (del test anterior)
        exists_true = articulo_crud.exists_by_rtr_id(99999)
        print(f"   ✅ RTR_ID 99999 existe: {exists_true}")
        
        # Probar con un ID que no debería existir
        exists_false = articulo_crud.exists_by_rtr_id(999999999)
        print(f"   ✅ RTR_ID 999999999 existe: {exists_false}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_articulo_get_by_id():
    """Probar obtener artículo por ID"""
    print("\n🧪 TEST: articulo_crud.get_by_id()")
    
    try:
        # Buscar artículo que debería existir
        articulo = articulo_crud.get_by_id(99999)
        
        if articulo:
            print(f"   ✅ Artículo encontrado:")
            print(f"      ID: {articulo.id}")
            print(f"      RTR_ID: {articulo.rtr_id}")
            print(f"      Nombre: {articulo.nombre}")
            print(f"      Precio: {articulo.precio}")
        else:
            print("   ❌ No se encontró el artículo")
            
        # Buscar artículo que no debería existir
        articulo_inexistente = articulo_crud.get_by_id(999999999)
        print(f"   ✅ Artículo inexistente: {articulo_inexistente}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_historial_insert_one():
    """Probar insertar un precio"""
    print("\n🧪 TEST: historial_crud.insert_one()")
    
    price_data = {
        'rtr_id': 99999,
        'precio': 159.99,
        'fecha': '2025-07-06',
        'fuente': 'test_individual'
    }
    
    try:
        result = historial_crud.insert_one(price_data)
        print(f"   ✅ Precio insertado: {result}")
        
        # Verificar que se insertó
        exists = historial_crud.exists_for_date(99999, '2025-07-06')
        print(f"   ✅ Verificación de existencia: {exists}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_historial_bulk_insert():
    """Probar inserción masiva de precios"""
    print("\n🧪 TEST: historial_crud.bulk_insert()")
    
    prices_list = [
        {
            'rtr_id': 88881,
            'precio': 45.00,
            'fecha': '2025-07-01',
            'fuente': 'test_bulk'
        },
        {
            'rtr_id': 88881,
            'precio': 47.50,
            'fecha': '2025-07-02',
            'fuente': 'test_bulk'
        },
        {
            'rtr_id': 88882,
            'precio': 70.00,
            'fecha': '2025-07-01',
            'fuente': 'test_bulk'
        },
        {
            'rtr_id': 88882,
            'precio': 72.50,
            'fecha': '2025-07-03',
            'fuente': 'test_bulk'
        }
    ]
    
    try:
        result = historial_crud.bulk_insert(prices_list)
        print(f"   ✅ Precios insertados: {result}")
        
        # Verificar algunos
        exists1 = historial_crud.exists_for_date(88881, '2025-07-01')
        exists2 = historial_crud.exists_for_date(88882, '2025-07-03')
        print(f"   ✅ RTR_ID 88881 fecha 2025-07-01: {exists1}")
        print(f"   ✅ RTR_ID 88882 fecha 2025-07-03: {exists2}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_historial_exists_for_date():
    """Probar verificación de existencia por fecha"""
    print("\n🧪 TEST: historial_crud.exists_for_date()")
    
    try:
        # Probar con fecha que debería existir
        exists_true = historial_crud.exists_for_date(99999, '2025-07-06')
        print(f"   ✅ RTR_ID 99999 fecha 2025-07-06: {exists_true}")
        
        # Probar con fecha que no debería existir
        exists_false = historial_crud.exists_for_date(99999, '2020-01-01')
        print(f"   ✅ RTR_ID 99999 fecha 2020-01-01: {exists_false}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_historial_get_dates_by_rtr_id():
    """Probar obtener fechas por RTR ID"""
    print("\n🧪 TEST: historial_crud.get_dates_by_rtr_id()")
    
    try:
        # Obtener fechas para RTR_ID que debería tener datos
        fechas = historial_crud.get_dates_by_rtr_id(88881)
        print(f"   ✅ Fechas para RTR_ID 88881: {fechas}")
        
        # Obtener fechas para RTR_ID que no debería tener datos
        fechas_vacias = historial_crud.get_dates_by_rtr_id(999999999)
        print(f"   ✅ Fechas para RTR_ID inexistente: {fechas_vacias}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def cleanup_test_data():
    """Limpiar datos de prueba"""
    print("\n🧹 CLEANUP: Eliminando datos de prueba...")
    
    try:
        from database.db_session import db_manager
        with db_manager.get_session() as session:
            # IDs de prueba utilizados
            test_rtr_ids = [99999, 88881, 88882, 88883]
            
            # Eliminar precios de prueba
            from database.db_models import HistorialPrecio, Articulo
            for rtr_id in test_rtr_ids:
                deleted_prices = session.query(HistorialPrecio).filter(HistorialPrecio.rtr_id == rtr_id).delete()
                deleted_articles = session.query(Articulo).filter(Articulo.rtr_id == rtr_id).delete()
                print(f"   🗑️  RTR_ID {rtr_id}: {deleted_prices} precios, {deleted_articles} artículos eliminados")
            
            session.commit()
            print("   ✅ Cleanup completado")
            
    except Exception as e:
        print(f"   ❌ Error en cleanup: {e}")

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DE CRUD_OPERATIONS")
    print("=" * 60)
    
    # Pruebas de ArticuloCRUD
    print("\n📦 PRUEBAS DE ARTICULO_CRUD")
    print("-" * 40)
    test_articulo_get_all()
    test_articulo_insert_one()
    test_articulo_bulk_insert()
    test_articulo_exists_by_rtr_id()
    test_articulo_get_by_id()
    
    # Pruebas de HistorialCRUD
    print("\n💰 PRUEBAS DE HISTORIAL_CRUD")
    print("-" * 40)
    test_historial_insert_one()
    test_historial_bulk_insert()
    test_historial_exists_for_date()
    test_historial_get_dates_by_rtr_id()
    
    # Cleanup
    cleanup_test_data()
    
    print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()