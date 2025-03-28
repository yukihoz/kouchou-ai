import { promises as fs } from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const defaultDir = path.join(__dirname, '../../server/public/meta/default')
const customDir = path.join(__dirname, '../../server/public/meta/custom')
const destDir = path.join(__dirname, '../public/meta')

async function copyImages() {
  try {
    await fs.mkdir(destDir, { recursive: true })

    const defaultFiles = await fs.readdir(defaultDir)
    const customFiles = await fs.readdir(customDir)

    await Promise.all(
      defaultFiles.map(async (file) => {
        const sourceFile = path.join(defaultDir, file)
        const destFile = path.join(destDir, file)
        await fs.copyFile(sourceFile, destFile)
        console.log(`Copied from default: ${file}`)
      })
    )

    await Promise.all(
      customFiles.map(async (file) => {
        const sourceFile = path.join(customDir, file)
        const destFile = path.join(destDir, file)
        await fs.copyFile(sourceFile, destFile)
        console.log(`Overwritten from custom: ${file}`)
      })
    )

    console.log('✅ All images copied successfully.')
  } catch (error) {
    console.error('❌ Error copying images:', error)
  }
}

copyImages()
