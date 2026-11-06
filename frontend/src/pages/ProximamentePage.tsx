import { Card, CardContent } from '@/components/ui/card'

export function ProximamentePage({ titulo }: { titulo: string }) {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{titulo}</h1>
      <Card>
        <CardContent className="text-muted-foreground">
          Esta sección todavía no está lista. Llegará en una fase posterior del proyecto.
        </CardContent>
      </Card>
    </div>
  )
}
