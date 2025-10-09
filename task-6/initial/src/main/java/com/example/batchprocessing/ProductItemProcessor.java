package com.example.batchprocessing;

import org.springframework.batch.item.ItemProcessor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.springframework.dao.EmptyResultDataAccessException;

@Component
public class ProductItemProcessor implements ItemProcessor<Product, Product> {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Override
    public Product process(final Product product) throws Exception {
        // Получаем данные лояльности из таблицы loyality_data
        String loyalityData = getLoyalityData(product.productSku());

        // Обновляем productData с информацией о лояльности
        String updatedProductData = truncateProductData(
            product.productData() + " | Loyality: " + loyalityData
        );

        // Обрезаем productName до 20 символов если нужно
        String truncatedProductName = truncateProductName(product.productName());

        return new Product(
            product.productId(),
            product.productSku(),
            truncatedProductName,
            product.productAmount(),
            updatedProductData
        );
    }

    private String getLoyalityData(Long productSku) {
        String sql = "SELECT loyalityData FROM loyality_data WHERE productSku = ?";

        try {
            String result = jdbcTemplate.queryForObject(sql, String.class, productSku);
            return result != null ? result : "No loyality data";
        } catch (EmptyResultDataAccessException e) {
            return "No loyality data";
        } catch (Exception e) {
            return "Error fetching loyality data";
        }
    }

    private String truncateProductData(String productData) {
        if (productData != null && productData.length() > 120) {
            return productData.substring(0, 117) + "...";
        }
        return productData;
    }

    private String truncateProductName(String productName) {
        if (productName != null && productName.length() > 20) {
            return productName.substring(0, 17) + "...";
        }
        return productName;
    }
}