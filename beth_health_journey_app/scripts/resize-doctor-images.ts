import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';

// Configuration
const IMAGE_DIRECTORY = path.join(process.cwd(), 'public', 'doctor-images');
const TARGET_WIDTH = 300; // Width in pixels
const TARGET_HEIGHT = 300; // Height in pixels
const QUALITY = 95; // JPEG quality (0-100)

async function enhanceImages() {
  console.log('🖼️ DOCTOR IMAGE ENHANCER 🖼️');
  console.log('=============================');
  console.log(`Enhancing all doctor images to improve quality`);
  console.log(`Final size will be ${TARGET_WIDTH}x${TARGET_HEIGHT} pixels`);
  console.log(`Image directory: ${IMAGE_DIRECTORY}`);
  console.log('');

  try {
    // Read all files in the directory
    const files = fs.readdirSync(IMAGE_DIRECTORY);
    
    // Filter for image files only
    const imageFiles = files.filter(file => {
      const ext = path.extname(file).toLowerCase();
      return ext === '.jpg' || ext === '.jpeg' || ext === '.png' || ext === '.webp';
    });
    
    console.log(`Found ${imageFiles.length} image files to enhance`);
    
    // Process each image
    for (let i = 0; i < imageFiles.length; i++) {
      const filename = imageFiles[i];
      const filePath = path.join(IMAGE_DIRECTORY, filename);
      
      // Skip directories
      if (fs.statSync(filePath).isDirectory()) {
        continue;
      }
      
      console.log(`Enhancing image ${i+1}/${imageFiles.length}: ${filename}`);
      
      // Apply enhancement and processing
      try {
        await sharp(filePath)
          // First upscale to higher resolution than target
          .resize({
            width: TARGET_WIDTH * 2,
            height: TARGET_HEIGHT * 2,
            fit: 'fill',
            kernel: 'lanczos3' // Better quality upscaling
          })
          // Apply light sharpening to enhance details
          .sharpen({
            sigma: 1.0,  // Sharpening radius
            m1: 1.0,     // Sharpening strength
            m2: 1.5,     // Detail level
            x1: 5,       // Threshold for edge detection
            y2: 20       // Threshold for detail detection
          })
          // Improve clarity
          .modulate({
            lightness: 1.05, // Slightly brighten
            saturation: 1.1  // Slightly increase saturation
          })
          // Reduce noise while preserving edges
          .recomb([
            [0.95, 0.025, 0.025],
            [0.025, 0.95, 0.025],
            [0.025, 0.025, 0.95]
          ])
          // Apply mild median filter to reduce noise (especially in face images)
          .median(1)
          // Now resize to target size
          .resize({
            width: TARGET_WIDTH,
            height: TARGET_HEIGHT,
            fit: 'cover',
            position: 'top'
          })
          // Save with high quality
          .jpeg({ quality: QUALITY, force: true })
          .toFile(path.join(IMAGE_DIRECTORY, `enhanced_${filename}`));
          
        // Replace original with enhanced version
        fs.unlinkSync(filePath);
        fs.renameSync(path.join(IMAGE_DIRECTORY, `enhanced_${filename}`), filePath);
        
        console.log(`  ✨ Successfully enhanced ${filename}`);
      } catch (imageError) {
        console.error(`  ❌ Error enhancing ${filename}:`, imageError);
      }
    }
    
    console.log('');
    console.log('✅ Image enhancement process complete!');
    console.log(`All images have been enhanced and normalized to ${TARGET_WIDTH}x${TARGET_HEIGHT} pixels`);
    
  } catch (error) {
    console.error('Error processing images:', error);
  }
}

// Run the function
enhanceImages(); 